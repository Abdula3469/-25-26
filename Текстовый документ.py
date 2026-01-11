# ollama_sparql.py
import requests
import json
import re

class OllamaSPARQLGenerator:
    def __init__(self, model="mistral-sparql"):
        self.model = model
        self.base_url = "http://localhost:11434"
        
    def clean_response(self, text):
        """Очистка ответа модели"""
        # Удаляем markdown если есть
        text = re.sub(r'```sparql\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Ищем начало SPARQL запроса
        lines = text.strip().split('\n')
        sparql_lines = []
        in_query = False
        
        for line in lines:
            # Начало SPARQL запроса
            if line.startswith(('PREFIX', 'SELECT', 'ASK', 'CONSTRUCT', 'DESCRIBE')):
                in_query = True
                
            if in_query:
                sparql_lines.append(line)
                
            # Конец запроса - пустая строка или что-то не SPARQL
            if in_query and line.strip() == '' and len(sparql_lines) > 5:
                break
        
        result = '\n'.join(sparql_lines).strip()
        
        # Убеждаемся, что есть обязательные префиксы
        if 'PREFIX wd:' not in result:
            result = "PREFIX wd: <http://www.wikidata.org/entity/>\n" + result
        if 'PREFIX wdt:' not in result:
            result = "PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n" + result
            
        return result
    
    def generate_sparql(self, user_query):
        """Генерация SPARQL запроса"""
        prompt = f"""
Ты — эксперт по Wikidata и SPARQL. Преобразуй запрос в SPARQL.

ЗАПРОС: {user_query}

Сгенерируй SPARQL запрос для Wikidata.
Используй префиксы wd: и wdt:.
Добавь SERVICE wikibase:label для получения меток.
Ответ должен содержать только SPARQL запрос.
"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 512,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result.get('response', '')
                return self.clean_response(raw_response)
            else:
                return f"Ошибка: {response.status_code}"
                
        except Exception as e:
            return f"Ошибка соединения: {str(e)}"
    
    def test_queries(self, test_queries):
        """Тестирование на наборе запросов"""
        results = []
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Запрос: {query}")
            
            sparql = self.generate_sparql(query)
            print(f"Сгенерированный SPARQL:\n{sparql}")
            
            # Простая валидация
            if "SELECT" in sparql and "WHERE" in sparql:
                print("✅ Базовая проверка пройдена")
            else:
                print("❌ Возможна ошибка в формате")
            
            results.append({
                "query": query,
                "sparql": sparql
            })
        
        return results

# Использование
if __name__ == "__main__":
    generator = OllamaSPARQLGenerator()
    
    test_queries = [
        "Найди российских космонавтов",
        "Покажи университеты в Москве",
        "Найди фильмы 2023 года",
        "Сколько городов в Германии?",
        "Найди картины Леонардо да Винчи"
    ]
    
    generator.test_queries(test_queries)