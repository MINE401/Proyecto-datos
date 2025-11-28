#!/usr/bin/env python3
"""
Script de test para verificar que la aplicación está corriendo correctamente.
Valida:
1. La conexión a la base de datos
2. El estado de los endpoints de la API
3. Que las tablas existan en la BD
"""

import requests
import psycopg2
from psycopg2 import sql
import time
import sys
from datetime import datetime

# Configuración
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "user"
DB_PASSWORD = "password"
DB_NAME = "partner_db"
API_URL = "http://localhost:8000"
MAX_RETRIES = 5
RETRY_DELAY = 2

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def test_database_connection():
    """Test 1: Validar conexión a PostgreSQL"""
    print_header("TEST 1: Conexión a Base de Datos")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5
        )
        cursor = conn.cursor()
        
        print_success(f"Conexión a PostgreSQL establecida")
        print_info(f"  Host: {DB_HOST}:{DB_PORT}")
        print_info(f"  Base de datos: {DB_NAME}")
        print_info(f"  Usuario: {DB_USER}")
        
        # Obtener información de la BD
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_info(f"  Versión: {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print_error(f"Error al conectar a PostgreSQL: {str(e)}")
        return False

def test_database_tables():
    """Test 2: Validar que las tablas existan"""
    print_header("TEST 2: Validación de Tablas en BD")
    
    expected_tables = [
        "company",
        "industry",
        "partner_classification",
        "cloud",
        "location",
        "partner_vendor",
        "technology_sc",
        "technology",
        "score"
    ]
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print_info(f"Tablas encontradas: {len(existing_tables)}")
        
        all_exist = True
        for table in expected_tables:
            if table in existing_tables:
                print_success(f"Tabla '{table}' existe")
            else:
                print_error(f"Tabla '{table}' no existe")
                all_exist = False
        
        # Mostrar tabla de resumen
        print(f"\n{Colors.BLUE}Resumen de Tablas:{Colors.END}")
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        print(f"\n{'Tabla':<30} {'Tamaño':<15}")
        print("-" * 45)
        for row in cursor.fetchall():
            print(f"{row[1]:<30} {row[2]:<15}")
        
        cursor.close()
        conn.close()
        return all_exist
    except Exception as e:
        print_error(f"Error al validar tablas: {str(e)}")
        return False

def test_api_health():
    """Test 3: Validar que la API esté disponible"""
    print_header("TEST 3: Disponibilidad de API")
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(f"{API_URL}/docs", timeout=5)
            if response.status_code == 200:
                print_success(f"API disponible en {API_URL}")
                print_info(f"  Documentación Swagger: {API_URL}/docs")
                return True
            else:
                print_warning(f"API respondió con status {response.status_code}")
        except requests.exceptions.ConnectionError:
            retries += 1
            if retries < MAX_RETRIES:
                print_warning(f"API no disponible. Reintentando ({retries}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
        except Exception as e:
            print_warning(f"Error al conectar a API: {str(e)}")
    
    print_error(f"No se pudo conectar a la API en {API_URL}")
    return False

def test_api_endpoint():
    """Test 4: Probar endpoint /query"""
    print_header("TEST 4: Prueba de Endpoint /query")
    
    try:
        # Query para listar compañías
        payload = {
            "action": "list_companies",
            "params": {},
            "pagination": {
                "limit": 10,
                "offset": 0
            }
        }
        
        response = requests.post(f"{API_URL}/query", json=payload, timeout=10)
        
        if response.status_code == 200:
            print_success(f"Endpoint /query respondió correctamente")
            data = response.json()
            print_info(f"  Respuesta: {len(data)} registros encontrados")
            
            if isinstance(data, list) and len(data) > 0:
                print_info(f"  Primer registro: {str(data[0])[:80]}...")
            
            return True
        else:
            print_error(f"Endpoint /query respondió con status {response.status_code}")
            print_info(f"  Respuesta: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Error al probar endpoint: {str(e)}")
        return False

def test_api_endpoints_health():
    """Test 5: Revisar estado de OpenAPI"""
    print_header("TEST 5: Información de la API")
    
    try:
        response = requests.get(f"{API_URL}/openapi.json", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"OpenAPI Schema disponible")
            print_info(f"  Título: {data.get('info', {}).get('title', 'N/A')}")
            print_info(f"  Descripción: {data.get('info', {}).get('description', 'N/A')[:60]}")
            print_info(f"  Versión: {data.get('info', {}).get('version', 'N/A')}")
            print_info(f"  Endpoints: {len(data.get('paths', {}))}")
            
            return True
        else:
            print_error(f"No se pudo obtener OpenAPI Schema")
            return False
    except Exception as e:
        print_warning(f"Error al obtener OpenAPI Schema: {str(e)}")
        return False

def generate_summary(results):
    """Generar resumen final"""
    print_header("RESUMEN DE TESTS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{'Test':<40} {'Resultado':<15}")
    print("-" * 55)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✓ PASÓ{Colors.END}" if result else f"{Colors.RED}✗ FALLÓ{Colors.END}"
        print(f"{test_name:<40} {status}")
    
    print("\n" + "="*55)
    percentage = (passed / total) * 100
    
    if passed == total:
        print_success(f"TODOS LOS TESTS PASARON ({passed}/{total}) - {percentage:.0f}%")
    elif passed >= total * 0.75:
        print_warning(f"MAYORÍA DE TESTS PASARON ({passed}/{total}) - {percentage:.0f}%")
    else:
        print_error(f"VARIOS TESTS FALLARON ({passed}/{total}) - {percentage:.0f}%")
    
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    print("\n" + Colors.BLUE + "╔" + "="*58 + "╗" + Colors.END)
    print(Colors.BLUE + "║" + " "*58 + "║" + Colors.END)
    print(Colors.BLUE + "║" + "  TEST SUITE - Validación de Aplicación".center(58) + "║" + Colors.END)
    print(Colors.BLUE + "║" + " "*58 + "║" + Colors.END)
    print(Colors.BLUE + "╚" + "="*58 + "╝" + Colors.END + "\n")
    
    results = {}
    
    # Ejecutar tests
    results["1. Conexión a BD"] = test_database_connection()
    
    if results["1. Conexión a BD"]:
        results["2. Tablas en BD"] = test_database_tables()
    else:
        print_error("Saltando tests de BD por fallos de conexión")
        results["2. Tablas en BD"] = False
    
    results["3. Disponibilidad API"] = test_api_health()
    
    if results["3. Disponibilidad API"]:
        results["4. Endpoint /query"] = test_api_endpoint()
        results["5. OpenAPI Schema"] = test_api_endpoints_health()
    else:
        print_warning("Saltando tests de API por falta de disponibilidad")
        results["4. Endpoint /query"] = False
        results["5. OpenAPI Schema"] = False
    
    # Resumen
    generate_summary(results)
    
    # Exit code basado en resultados
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
