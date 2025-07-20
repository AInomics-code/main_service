import json
import os

def generate_schema_files(json_data: dict, output_folder: str = "schema_files"):
    """
    Genera archivos txt de esquema basados en el JSON de la base de datos.
    
    Args:
        json_data: Diccionario con la información de la base de datos
        output_folder: Carpeta donde guardar los archivos txt
    """
    
    # Crear carpeta si no existe
    os.makedirs(output_folder, exist_ok=True)
    
    tables = json_data.get("tables", [])
    
    for table in tables:
        table_name = table.get("table_name", "")
        description = table.get("description", "")
        columns = table.get("columns", [])
        
        # Crear contenido del archivo
        content = f"TABLA: {table_name}\n"
        
        if description:
            content += f"DESCRIPCIÓN: {description}\n"
        
        content += f"\nCOLUMNAS:\n"
        
        for column in columns:
            col_name = column.get("column_name", "")
            col_type = column.get("data_type", "")
            col_description = column.get("description", "")
            
            content += f"- {col_name} ({col_type})"
            if col_description:
                content += f": {col_description}"
            content += "\n"
        
        # Guardar archivo
        file_path = os.path.join(output_folder, f"{table_name}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Archivo generado: {file_path}")

def main():
    """
    Función principal que genera los archivos de esquema.
    """
    
    # JSON de la base de datos (el que proporcionaste)
    db_schema = {
        "database_name": "la_dona?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes",
        "tables": [
            {
                "table_name": "area_de_despacho",
                "description": "Tabla que contiene las áreas de despacho disponibles en el sistema",
                "columns": [
                    {"column_name": "codigo_de_area_de_despacho", "data_type": "numeric", "description": "Código único identificador del área de despacho"},
                    {"column_name": "descripcion", "data_type": "nvarchar", "description": "Descripción o nombre del área de despacho"}
                ]
            },
            {
                "table_name": "backorder",
                "description": "Tabla que registra los pedidos pendientes o backorders del sistema",
                "columns": [
                    {"column_name": "numero_de_pedsido", "data_type": "nvarchar", "description": "Número único del pedido"},
                    {"column_name": "fecha_de_pedido", "data_type": "datetime", "description": "Fecha en que se realizó el pedido"},
                    {"column_name": "codigo_de_cliente", "data_type": "nvarchar", "description": "Código del cliente que realizó el pedido"},
                    {"column_name": "codigo_de_vendedor", "data_type": "nvarchar", "description": "Código del vendedor asignado"},
                    {"column_name": "numero_de_factura", "data_type": "nvarchar", "description": "Número de factura asociado"},
                    {"column_name": "linea", "data_type": "int", "description": "Número de línea del pedido"},
                    {"column_name": "codigo_de_producto", "data_type": "nvarchar", "description": "Código del producto solicitado"},
                    {"column_name": "cantidad_perdida", "data_type": "numeric", "description": "Cantidad perdida del pedido"},
                    {"column_name": "cantidad_entregada", "data_type": "numeric", "description": "Cantidad ya entregada"},
                    {"column_name": "cantidad_pendiente", "data_type": "numeric", "description": "Cantidad pendiente por entregar"},
                    {"column_name": "precio", "data_type": "numeric", "description": "Precio unitario del producto"},
                    {"column_name": "porcentaje_de_descuento", "data_type": "numeric", "description": "Porcentaje de descuento aplicado"},
                    {"column_name": "codigo_de_tipo", "data_type": "nvarchar", "description": "Código del tipo de producto"},
                    {"column_name": "porcentaje_de_impuesto", "data_type": "numeric", "description": "Porcentaje de impuesto aplicado"},
                    {"column_name": "codigo_de_deposito", "data_type": "nvarchar", "description": "Código del depósito de origen"},
                    {"column_name": "codigo_de_clase", "data_type": "nvarchar", "description": "Código de la clase del producto"},
                    {"column_name": "factor_de_conversion", "data_type": "int", "description": "Factor de conversión de unidades"},
                    {"column_name": "costo", "data_type": "numeric", "description": "Costo unitario del producto"},
                    {"column_name": "fecha_de_la_factura", "data_type": "datetime", "description": "Fecha de la factura"},
                    {"column_name": "codigo_supervisor_trade", "data_type": "nvarchar", "description": "Código del supervisor trade"}
                ]
            },
            {
                "table_name": "canales",
                "description": "Tabla que define los diferentes canales de venta",
                "columns": [
                    {"column_name": "codigo_de_canal", "data_type": "nvarchar", "description": "Código único del canal"},
                    {"column_name": "nombre_de_canal", "data_type": "nvarchar", "description": "Nombre descriptivo del canal"}
                ]
            },
            {
                "table_name": "categorias",
                "description": "Tabla que contiene las categorías de productos",
                "columns": [
                    {"column_name": "codigo_de_categoria", "data_type": "nvarchar", "description": "Código único de la categoría"},
                    {"column_name": "nombre_de_categoria", "data_type": "nvarchar", "description": "Nombre de la categoría"}
                ]
            },
            {
                "table_name": "clases",
                "description": "Tabla que define las clases de productos dentro de las categorías",
                "columns": [
                    {"column_name": "codigo_de_clase", "data_type": "nvarchar", "description": "Código único de la clase"},
                    {"column_name": "nombre_de_clase", "data_type": "nvarchar", "description": "Nombre de la clase"},
                    {"column_name": "codigo_de_tipo", "data_type": "nvarchar", "description": "Código del tipo asociado"},
                    {"column_name": "codigo_de_categoria", "data_type": "nvarchar", "description": "Código de la categoría a la que pertenece"}
                ]
            },
            {
                "table_name": "clientes",
                "description": "Tabla principal de clientes del sistema con información completa de contacto y comercial",
                "columns": [
                    {"column_name": "codigo_de_cliente", "data_type": "nvarchar", "description": "Código único del cliente"},
                    {"column_name": "codigo_de_grupo", "data_type": "nvarchar", "description": "Código del grupo al que pertenece el cliente"},
                    {"column_name": "nombre_de_cliente", "data_type": "nvarchar", "description": "Nombre del cliente"},
                    {"column_name": "direccion", "data_type": "nvarchar", "description": "Dirección física del cliente"},
                    {"column_name": "dia_de_recibo", "data_type": "nvarchar", "description": "Día preferido para recibir pedidos"},
                    {"column_name": "hora_de_recibo", "data_type": "nvarchar", "description": "Hora preferida para recibir pedidos"},
                    {"column_name": "ciudad", "data_type": "nvarchar", "description": "Ciudad del cliente"},
                    {"column_name": "pais", "data_type": "nvarchar", "description": "País del cliente"},
                    {"column_name": "mercaderista", "data_type": "nvarchar", "description": "Mercaderista asignado al cliente"},
                    {"column_name": "telefono1", "data_type": "nvarchar", "description": "Teléfono principal"},
                    {"column_name": "telefono2", "data_type": "nvarchar", "description": "Teléfono secundario"},
                    {"column_name": "fecha_de_inactivo", "data_type": "nvarchar", "description": "Fecha en que el cliente se volvió inactivo"},
                    {"column_name": "telefono_para_recibo", "data_type": "nvarchar", "description": "Teléfono para recibir pedidos"},
                    {"column_name": "codigo_de_provincia", "data_type": "nvarchar", "description": "Código de la provincia"},
                    {"column_name": "inicia_atencion_trade", "data_type": "nvarchar", "description": "Hora de inicio de atención trade"},
                    {"column_name": "fin_de_atencion_trade", "data_type": "nvarchar", "description": "Hora de fin de atención trade"},
                    {"column_name": "codigo_de_distrito", "data_type": "nvarchar", "description": "Código del distrito"},
                    {"column_name": "contacto", "data_type": "nvarchar", "description": "Nombre del contacto principal"},
                    {"column_name": "codigo_de_corregimiento", "data_type": "nvarchar", "description": "Código del corregimiento"},
                    {"column_name": "codigo_de_vendedor", "data_type": "nvarchar", "description": "Código del vendedor asignado"},
                    {"column_name": "paga_impuesto", "data_type": "nvarchar", "description": "Indica si el cliente paga impuestos"},
                    {"column_name": "limite_de_credito", "data_type": "numeric", "description": "Límite de crédito del cliente"},
                    {"column_name": "condicion_de_pago", "data_type": "nvarchar", "description": "Condición de pago del cliente"},
                    {"column_name": "dias_para_morosidad", "data_type": "int", "description": "Días para considerar morosidad"},
                    {"column_name": "cuenta", "data_type": "nvarchar", "description": "Número de cuenta del cliente"},
                    {"column_name": "ruc", "data_type": "nvarchar", "description": "RUC del cliente"},
                    {"column_name": "digito_verificador", "data_type": "nvarchar", "description": "Dígito verificador del RUC"},
                    {"column_name": "estado", "data_type": "nvarchar", "description": "Estado del cliente (activo/inactivo)"},
                    {"column_name": "fecha_de_creacion", "data_type": "datetime", "description": "Fecha de creación del cliente"},
                    {"column_name": "precio_de_lista", "data_type": "nvarchar", "description": "Tipo de precio de lista del cliente"},
                    {"column_name": "email", "data_type": "nvarchar", "description": "Email del cliente"},
                    {"column_name": "codigo_supervisor_trade", "data_type": "nvarchar", "description": "Código del supervisor trade"},
                    {"column_name": "saldo", "data_type": "numeric", "description": "Saldo actual del cliente"},
                    {"column_name": "codigo_de_tipo_de_negocio", "data_type": "nvarchar", "description": "Código del tipo de negocio"},
                    {"column_name": "compra_al_detal", "data_type": "nvarchar", "description": "Indica si compra al detalle"},
                    {"column_name": "codigo_de_ruta", "data_type": "nvarchar", "description": "Código de la ruta asignada"},
                    {"column_name": "latitud", "data_type": "float", "description": "Latitud geográfica del cliente"},
                    {"column_name": "longitud", "data_type": "float", "description": "Longitud geográfica del cliente"},
                    {"column_name": "codigo_de_gestor_de_cobros", "data_type": "nvarchar", "description": "Código del gestor de cobros"},
                    {"column_name": "codigo_de_pais", "data_type": "nvarchar", "description": "Código del país"},
                    {"column_name": "razon_social", "data_type": "nvarchar", "description": "Razón social del cliente"},
                    {"column_name": "tipo_de_receptor", "data_type": "nvarchar", "description": "Tipo de receptor fiscal"},
                    {"column_name": "codigo_de_cliente_de_enlace", "data_type": "nvarchar", "description": "Código del cliente de enlace"},
                    {"column_name": "codigo_de_gerente", "data_type": "nvarchar", "description": "Código del gerente asignado"},
                    {"column_name": "centro_de_distribucion", "data_type": "nvarchar", "description": "Centro de distribución asignado"},
                    {"column_name": "fecha_ultima_venta", "data_type": "datetime", "description": "Fecha de la última venta"},
                    {"column_name": "fecha_ultima_devolucion", "data_type": "datetime", "description": "Fecha de la última devolución"}
                ]
            },
            {
                "table_name": "ventas",
                "description": "Tabla principal de ventas. Usa esta tabla cuando quieras analizar las ventas por periodo. La venta bruta es igual a la sumatoria de la columnas importe_de_la_linea menos la sumatoria de descuento_de_la_linea",
                "columns": [
                    {"column_name": "documento", "data_type": "nvarchar", "description": "Número de documento de venta"},
                    {"column_name": "fecha", "data_type": "datetime", "description": "Fecha de la venta"},
                    {"column_name": "codigo_de_vendedor", "data_type": "nvarchar", "description": "Código del vendedor que realizó la venta"},
                    {"column_name": "tipo_de_transaccion", "data_type": "nvarchar", "description": "Tipo de transacción (venta, devolución, etc.)"},
                    {"column_name": "cantidad", "data_type": "numeric", "description": "Cantidad vendida"},
                    {"column_name": "precio", "data_type": "numeric", "description": "Precio unitario"},
                    {"column_name": "costo", "data_type": "numeric", "description": "Costo unitario"},
                    {"column_name": "codigo_de_cliente", "data_type": "nvarchar", "description": "Código del cliente"},
                    {"column_name": "codigo_de_producto", "data_type": "nvarchar", "description": "Código del producto vendido"},
                    {"column_name": "porcentaje_de_descuento", "data_type": "numeric", "description": "Porcentaje de descuento aplicado"},
                    {"column_name": "porcentaje_de_impuesto", "data_type": "numeric", "description": "Porcentaje de impuesto aplicado"},
                    {"column_name": "codigo_de_deposito", "data_type": "nvarchar", "description": "Código del depósito de origen"},
                    {"column_name": "factor_de_conversion", "data_type": "numeric", "description": "Factor de conversión de unidades"},
                    {"column_name": "porcentaje_de_descuento_adicional", "data_type": "numeric", "description": "Porcentaje de descuento adicional"},
                    {"column_name": "descuento_de_la_linea", "data_type": "numeric", "description": "Monto del descuento de la línea"},
                    {"column_name": "impuesto_de_la_linea", "data_type": "numeric", "description": "Monto del impuesto de la línea"},
                    {"column_name": "importe_de_la_linea", "data_type": "numeric", "description": "Importe total de la línea"},
                    {"column_name": "costo_de_la_linea", "data_type": "numeric", "description": "Costo total de la línea"},
                    {"column_name": "descuento_adicional_de_la_linea", "data_type": "numeric", "description": "Descuento adicional de la línea"},
                    {"column_name": "monto_de_la_linea", "data_type": "numeric", "description": "Monto final de la línea"},
                    {"column_name": "lote", "data_type": "nvarchar", "description": "Número de lote del producto"},
                    {"column_name": "codigo_de_motivo_de_devolucion", "data_type": "nvarchar", "description": "Código del motivo de devolución"},
                    {"column_name": "documento_fiscal", "data_type": "nvarchar", "description": "Número de documento fiscal"},
                    {"column_name": "serie_fiscal", "data_type": "nvarchar", "description": "Serie del documento fiscal"},
                    {"column_name": "monto_impuesto_fiscal", "data_type": "numeric", "description": "Monto del impuesto fiscal"},
                    {"column_name": "monto_fiscal", "data_type": "numeric", "description": "Monto total fiscal"},
                    {"column_name": "codigo_de_transportista", "data_type": "nvarchar", "description": "Código del transportista"},
                    {"column_name": "fecha_de_vencimiento", "data_type": "datetime", "description": "Fecha de vencimiento del producto"},
                    {"column_name": "fecha_de_produccion", "data_type": "datetime", "description": "Fecha de producción del producto"}
                ]
            },
            {
                "table_name": "productos",
                "description": "Tabla principal de productos del sistema con información completa de precios, costos y características",
                "columns": [
                    {"column_name": "codigo_de_producto", "data_type": "nvarchar", "description": "Código único del producto"},
                    {"column_name": "nombre_de_producto", "data_type": "nvarchar", "description": "Nombre del producto"},
                    {"column_name": "unidad_de_medida", "data_type": "nvarchar", "description": "Unidad de medida del producto"},
                    {"column_name": "factor_de_inversion", "data_type": "numeric", "description": "Factor de inversión del producto"},
                    {"column_name": "tamano", "data_type": "nvarchar", "description": "Tamaño del producto"},
                    {"column_name": "codigo_de_barra", "data_type": "nvarchar", "description": "Código de barras del producto"},
                    {"column_name": "peso", "data_type": "float", "description": "Peso del producto"},
                    {"column_name": "estado", "data_type": "nvarchar", "description": "Estado del producto (activo/inactivo)"},
                    {"column_name": "costo", "data_type": "float", "description": "Costo del producto"},
                    {"column_name": "codigo_de_clase", "data_type": "nvarchar", "description": "Código de la clase del producto"},
                    {"column_name": "codigo_de_tipo", "data_type": "nvarchar", "description": "Código del tipo del producto"},
                    {"column_name": "codigo_de_impuesto", "data_type": "nvarchar", "description": "Código del impuesto aplicable"},
                    {"column_name": "origen", "data_type": "nvarchar", "description": "Origen del producto"},
                    {"column_name": "marca", "data_type": "nvarchar", "description": "Marca del producto"},
                    {"column_name": "fecha_de_creacion", "data_type": "datetime", "description": "Fecha de creación del producto"},
                    {"column_name": "modelo", "data_type": "nvarchar", "description": "Modelo del producto"},
                    {"column_name": "area", "data_type": "nvarchar", "description": "Área del producto"},
                    {"column_name": "perecedero", "data_type": "nvarchar", "description": "Indica si el producto es perecedero"},
                    {"column_name": "precio1", "data_type": "float", "description": "Precio 1 del producto"},
                    {"column_name": "precio2", "data_type": "float", "description": "Precio 2 del producto"},
                    {"column_name": "precio3", "data_type": "float", "description": "Precio 3 del producto"},
                    {"column_name": "precio4", "data_type": "float", "description": "Precio 4 del producto"},
                    {"column_name": "precio5", "data_type": "float", "description": "Precio 5 del producto"},
                    {"column_name": "precio6", "data_type": "float", "description": "Precio 6 del producto"},
                    {"column_name": "precio7", "data_type": "float", "description": "Precio 7 del producto"},
                    {"column_name": "precio8", "data_type": "float", "description": "Precio 8 del producto"},
                    {"column_name": "precio9", "data_type": "float", "description": "Precio 9 del producto"},
                    {"column_name": "precio10", "data_type": "float", "description": "Precio 10 del producto"},
                    {"column_name": "precio11", "data_type": "float", "description": "Precio 11 del producto"},
                    {"column_name": "precio12", "data_type": "float", "description": "Precio 12 del producto"},
                    {"column_name": "precio13", "data_type": "float", "description": "Precio 13 del producto"},
                    {"column_name": "precio14", "data_type": "float", "description": "Precio 14 del producto"},
                    {"column_name": "precio15", "data_type": "float", "description": "Precio 15 del producto"},
                    {"column_name": "precio16", "data_type": "float", "description": "Precio 16 del producto"},
                    {"column_name": "precio17", "data_type": "float", "description": "Precio 17 del producto"},
                    {"column_name": "precio18", "data_type": "float", "description": "Precio 18 del producto"},
                    {"column_name": "precio19", "data_type": "float", "description": "Precio 19 del producto"},
                    {"column_name": "precio20", "data_type": "float", "description": "Precio 20 del producto"},
                    {"column_name": "precio21", "data_type": "float", "description": "Precio 21 del producto"},
                    {"column_name": "precio22", "data_type": "float", "description": "Precio 22 del producto"},
                    {"column_name": "precio23", "data_type": "float", "description": "Precio 23 del producto"},
                    {"column_name": "precio24", "data_type": "float", "description": "Precio 24 del producto"},
                    {"column_name": "precio25", "data_type": "float", "description": "Precio 25 del producto"},
                    {"column_name": "precio26", "data_type": "float", "description": "Precio 26 del producto"},
                    {"column_name": "precio27", "data_type": "float", "description": "Precio 27 del producto"},
                    {"column_name": "precio28", "data_type": "float", "description": "Precio 28 del producto"},
                    {"column_name": "precio29", "data_type": "float", "description": "Precio 29 del producto"},
                    {"column_name": "precio30", "data_type": "float", "description": "Precio 30 del producto"},
                    {"column_name": "descuento_1", "data_type": "numeric", "description": "Descuento 1 aplicable"},
                    {"column_name": "descuento_2", "data_type": "numeric", "description": "Descuento 2 aplicable"},
                    {"column_name": "descuento_3", "data_type": "numeric", "description": "Descuento 3 aplicable"},
                    {"column_name": "descuento_4", "data_type": "numeric", "description": "Descuento 4 aplicable"},
                    {"column_name": "descuento_5", "data_type": "numeric", "description": "Descuento 5 aplicable"},
                    {"column_name": "descuento_6", "data_type": "numeric", "description": "Descuento 6 aplicable"},
                    {"column_name": "descuento_7", "data_type": "numeric", "description": "Descuento 7 aplicable"},
                    {"column_name": "descuento_8", "data_type": "numeric", "description": "Descuento 8 aplicable"},
                    {"column_name": "descuento_9", "data_type": "numeric", "description": "Descuento 9 aplicable"},
                    {"column_name": "descuento_10", "data_type": "numeric", "description": "Descuento 10 aplicable"},
                    {"column_name": "para_la_venta", "data_type": "nvarchar", "description": "Indica si el producto está disponible para la venta"},
                    {"column_name": "materia_prima", "data_type": "nvarchar", "description": "Indica si es materia prima"},
                    {"column_name": "fecha_de_registro_sanitario", "data_type": "date", "description": "Fecha del registro sanitario"},
                    {"column_name": "registro_sanitario", "data_type": "nvarchar", "description": "Número de registro sanitario"},
                    {"column_name": "kosher", "data_type": "nvarchar", "description": "Indica si el producto es kosher"},
                    {"column_name": "codigo_de_grupo_generico", "data_type": "numeric", "description": "Código del grupo genérico"},
                    {"column_name": "maneja_lotes", "data_type": "nvarchar", "description": "Indica si el producto maneja lotes"},
                    {"column_name": "codigo_de_categoria", "data_type": "nvarchar", "description": "Código de la categoría"},
                    {"column_name": "producto_de_enlace", "data_type": "nvarchar", "description": "Producto de enlace"},
                    {"column_name": "altura", "data_type": "numeric", "description": "Altura del producto"},
                    {"column_name": "ancho", "data_type": "numeric", "description": "Ancho del producto"},
                    {"column_name": "largo", "data_type": "numeric", "description": "Largo del producto"}
                ]
            }
        ]
    }
    
    # Generar archivos
    generate_schema_files(db_schema)
    print("Archivos de esquema generados exitosamente!")

if __name__ == "__main__":
    main() 