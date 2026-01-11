# final_test.py
import requests
import json
import time

class FixedSPARQLGenerator:
    def __init__(self, model_name="mistral-sparql-v2"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
    
    def generate(self, user_query):
        """Генерация SPARQL с постобработкой"""
        payload = {
            "model": self.model_name,
            "prompt": user_query,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 512,
                "top_p": 0.9
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                sparql = result.get('response', '').strip()
                
                sparql = self._fix_common_errors(sparql)
                
                return {
                    "success": True,
                    "sparql": sparql,
                    "time": response_time,
                    "raw": result.get('response', '')
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "time": response_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "time": 0
            }
    
    def _fix_common_errors(self, sparql):
        """Исправление частых ошибок в SPARQL"""
        if not sparql:
            return sparql
        
        if "wd:Q27692" in sparql:
            sparql = sparql.replace("wd:Q27692", "wd:Q515")  # Q515 = city
        
        sparql = sparql.replace('\\}', '}')
        
        lines = sparql.split('\n')
        fixed_lines = []
        for line in lines:
            if "FILTER(LANG(wd:Q" in line:
                line = '  FILTER(LANG(?label) = "de")'
            fixed_lines.append(line)
        
        if "LIMIT" not in sparql:
            sparql += "\nLIMIT 10"
        
        return '\n'.join(fixed_lines)
    
    def validate_sparql(self, sparql):
        """Проверка SPARQL на валидность"""
        if not sparql:
            return False, "Пустой запрос"
        
        required = [
            ("PREFIX wd:", "Нет префикса wd:"),
            ("PREFIX wdt:", "Нет префикса wdt:"),
            ("SELECT", "Нет SELECT"),
            ("WHERE", "Нет WHERE"),
            ("{", "Нет открывающей скобки WHERE"),
            ("}", "Нет закрывающей скобки WHERE")
        ]
        
        for check, error in required:
            if check not in sparql:
                return False, error
        
        if sparql.count("{") != sparql.count("}"):
            return False, "Непарные фигурные скобки"
        
        return True, "Валидный SPARQL"

# ТЕСТИРОВАНИЕ
def run_comprehensive_test():
    print(" КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ SPARQL ГЕНЕРАТОРА")
    print("=" * 70)
    
    generator = FixedSPARQLGenerator()
    
    test_cases = [
        ("Города Германии", "Должен содержать wdt:P17 wd:Q183"),
        ("Российские космонавты", "Должен содержать wdt:P106 wd:Q11631"),
        ("Реки длиннее 1000 км", "Должен содержать FILTER и wdt:P2043"),
        ("Сколько городов в Германии?", "Должен содержать COUNT"),
        ("Фильмы 2023 года", "Должен содержать wdt:P31 wd:Q11424"),
        ("Университеты в Москве", "Должен содержать wdt:P31 wd:Q3918"),
        ("Картины Ван Гога", "Должен содержать wdt:P170 wd:Q5582")
    ]
    
    for query, expectation in test_cases:
        print(f"\n{'='*70}")
        print(f" ЗАПРОС: {query}")
        print(f" ОЖИДАНИЕ: {expectation}")
        print(f"{'='*70}")
        
        result = generator.generate(query)
        
        if result["success"]:
            print(f" УСПЕХ! Время: {result['time']:.2f}с")
            print(f"\n SPARQL ЗАПРОС:")
            print("-" * 50)
            print(result["sparql"])
            print("-" * 50)
            
            is_valid, message = generator.validate_sparql(result["sparql"])
            if is_valid:
                print(f" {message}")
            else:
                print(f" {message}")
                
            if "WHERE {" in result["sparql"]:
                start = result["sparql"].find("WHERE {") + len("WHERE {")
                end = result["sparql"].find("}", start)
                where_content = result["sparql"][start:end].strip()
                
                if where_content:
                    print(f" Содержимое WHERE: {len(where_content)} символов")
                    triple_count = where_content.count(" wdt:")
                    print(f" Триплетов: {triple_count}")
                else:
                    print(" WHERE пустой!")
                    
        else:
            print(f" ОШИБКА: {result.get('error', 'Неизвестная ошибка')}")
    
    print(f"\n{'='*70}")
    print(" ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 70)

def interactive_mode():
    """Интерактивный режим работы"""
    print(" ИНТЕРАКТИВНЫЙ SPARQL ГЕНЕРАТОР")
    print("=" * 50)
    
    generator = FixedSPARQLGenerator()
    
    while True:
        print("\n" + "=" * 50)
        print("Введите запрос на естественном языке")
        print("Или 'выход' для завершения")
        print("=" * 50)
        
        user_input = input(">>> ").strip()
        
        if user_input.lower() in ['выход', 'exit', 'quit']:
            print("До свидания!")
            break
        
        if not user_input:
            continue
        
        print(f"\n Генерация SPARQL для: {user_input}")
        print(" Пожалуйста, подождите...")
        
        result = generator.generate(user_input)
        
        if result["success"]:
            print(f"\n СПАРКЛ сгенерирован за {result['time']:.2f}с")
            print("\n ЗАПРОС:")
            print("-" * 60)
            print(result["sparql"])
            print("-" * 60)
            
            execute = input("\n🔍 Выполнить запрос в Wikidata? (y/n): ").strip().lower()
            if execute == 'y':
                execute_sparql(result["sparql"])
        else:
            print(f"\n❌ ОШИБКА: {result.get('error', 'Неизвестная ошибка')}")

def execute_sparql(sparql_query):
    """Выполнение SPARQL запроса"""
    import requests
    
    print("\n Выполнение запроса в Wikidata...")
    
    try:
        endpoint = "https://query.wikidata.org/sparql"
        
        params = {
            'query': sparql_query,
            'format': 'json'
        }
        
        headers = {
            'User-Agent': 'SPARQLGeneratorTest/1.0',
            'Accept': 'application/sparql-results+json'
        }
        
        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {}).get('bindings', [])
            
            print(f"\n Найдено результатов: {len(results)}")
            
            if results:
                print("\n Первые 5 результатов:")
                for i, item in enumerate(results[:5], 1):
                    print(f"\n{i}.")
                    for key, value in item.items():
                        print(f"   {key}: {value.get('value', 'N/A')}")
        else:
            print(f"\n Ошибка выполнения: {response.status_code}")
            print(f"   {response.text[:200]}")
            
    except Exception as e:
        print(f"\n Ошибка: {str(e)}")

if __name__ == "__main__":
    print(" SPARQL ГЕНЕРАТОР v2.0")
    print("=" * 50)
    print("1. Запустить комплексное тестирование")
    print("2. Интерактивный режим")
    print("3. Тест одного запроса")
    print("=" * 50)
    
    choice = input("Выберите режим (1-3): ").strip()
    
    if choice == "1":
        run_comprehensive_test()
    elif choice == "2":
        interactive_mode()
    elif choice == "3":
        generator = FixedSPARQLGenerator()
        query = input("Введите тестовый запрос: ").strip()
        result = generator.generate(query)
        
        if result["success"]:
            print(f"\n Результат ({result['time']:.2f}с):")
            print(result["sparql"])
            
            is_valid, message = generator.validate_sparql(result["sparql"])
            print(f"\n Валидация: {message}")
        else:
            print(f" Ошибка: {result.get('error', 'Неизвестно')}")
    else:
        print(" Неверный выбор")