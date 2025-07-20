import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from typing import List, Dict, Any, Tuple
import glob

class SchemaSummarizer:
    """
    Herramienta para optimizar el envío de esquemas de base de datos a los agentes.
    Carga archivos txt de una carpeta y los indexa en una base de datos vectorial para búsqueda semántica.
    """
    
    def __init__(self, schema_folder: str = "schema_files", model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa el SchemaSummarizer.
        
        Args:
            schema_folder: Carpeta que contiene los archivos txt con descripciones de tablas
            model_name: Modelo de embeddings a usar
        """
        self.schema_folder = schema_folder
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.vectorstore = None
        self.documents = []
        self.table_names = []
        
    def load_schema_files(self) -> List[str]:
        """
        Carga todos los archivos txt de la carpeta de esquemas.
        
        Returns:
            Lista de rutas de archivos cargados
        """
        if not os.path.exists(self.schema_folder):
            raise FileNotFoundError(f"La carpeta {self.schema_folder} no existe")
        
        # Buscar todos los archivos txt en la carpeta
        txt_files = glob.glob(os.path.join(self.schema_folder, "*.txt"))
        
        if not txt_files:
            raise FileNotFoundError(f"No se encontraron archivos .txt en {self.schema_folder}")
        
        print(f"Encontrados {len(txt_files)} archivos de esquema")
        return txt_files
    
    def read_schema_file(self, file_path: str) -> Tuple[str, str]:
        """
        Lee un archivo de esquema y extrae el nombre de la tabla y su contenido.
        
        Args:
            file_path: Ruta al archivo txt
            
        Returns:
            Tupla con (nombre_tabla, contenido)
        """
        table_name = os.path.basename(file_path).replace('.txt', '')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        return table_name, content
    
    def build_vector_index(self):
        """
        Construye el índice vectorial con todos los archivos de esquema.
        """
        txt_files = self.load_schema_files()
        
        documents = []
        table_names = []
        
        for file_path in txt_files:
            table_name, content = self.read_schema_file(file_path)
            documents.append(content)
            table_names.append(table_name)
        
        if not documents:
            raise ValueError("No se pudieron cargar documentos de esquema")
        
        # Crear vectorstore con FAISS
        print("Generando embeddings y creando índice vectorial...")
        self.vectorstore = FAISS.from_texts(documents, self.embeddings)
        
        self.documents = documents
        self.table_names = table_names
        
        print(f"Índice vectorial construido con {len(documents)} tablas")
    
    def search_relevant_tables(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca las tablas más relevantes para una consulta dada.
        
        Args:
            query: Consulta del usuario
            top_k: Número máximo de resultados a retornar
            
        Returns:
            Lista de diccionarios con información de las tablas más relevantes
        """
        if self.vectorstore is None:
            raise ValueError("El índice vectorial no ha sido construido. Ejecuta build_vector_index() primero.")
        
        # Buscar en el vectorstore
        docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=top_k)
        
        results = []
        for i, (doc, score) in enumerate(docs_and_scores):
            # Encontrar el índice del documento en la lista original
            try:
                idx = self.documents.index(doc.page_content)
                table_name = self.table_names[idx]
            except ValueError:
                # Si no se encuentra, usar un índice por defecto
                idx = i
                table_name = f"table_{i}"
            
            results.append({
                'rank': i + 1,
                'table_name': table_name,
                'content': doc.page_content,
                'relevance_score': float(score),
                'file_path': os.path.join(self.schema_folder, f"{table_name}.txt")
            })
        
        return results
    
    def get_schema_summary(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Obtiene un resumen del esquema relevante para una consulta.
        
        Args:
            query: Consulta del usuario
            top_k: Número máximo de tablas a incluir
            
        Returns:
            Diccionario con el resumen del esquema
        """
        relevant_tables = self.search_relevant_tables(query, top_k)
        
        # Crear resumen estructurado
        summary = {
            'query': query,
            'relevant_tables': relevant_tables,
            'total_tables_found': len(relevant_tables),
            'schema_folder': self.schema_folder,
            'total_tables_in_index': len(self.table_names)
        }
        
        return summary
    
    def save_index(self, file_path: str):
        """
        Guarda el índice vectorial en disco.
        
        Args:
            file_path: Ruta donde guardar el índice
        """
        if self.vectorstore is None:
            raise ValueError("No hay índice para guardar")
        
        self.vectorstore.save_local(file_path)
        print(f"Índice guardado en {file_path}")
    
    def load_index(self, file_path: str, documents: List[str], table_names: List[str]):
        """
        Carga un índice vectorial desde disco.
        
        Args:
            file_path: Ruta del índice a cargar
            documents: Lista de documentos originales
            table_names: Lista de nombres de tablas
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo de índice {file_path} no existe")
        
        self.vectorstore = FAISS.load_local(file_path, self.embeddings)
        self.documents = documents
        self.table_names = table_names
        print(f"Índice cargado desde {file_path}")
    
    def list_all_tables(self) -> List[str]:
        """
        Lista todas las tablas en el índice.
        
        Returns:
            Lista de nombres de tablas
        """
        return self.table_names.copy()
    
    def get_table_content(self, table_name: str) -> str:
        """
        Obtiene el contenido de una tabla específica.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Contenido de la tabla
        """
        if table_name not in self.table_names:
            raise ValueError(f"Tabla '{table_name}' no encontrada en el índice")
        
        idx = self.table_names.index(table_name)
        return self.documents[idx] 