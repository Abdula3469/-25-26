1.  Скачайте Ollama
2.  Откройте PowerShell
3.  В новом окне PowerShell запустите сервер и оставьте его открытым, введя:
ollama serve

4.  Откройте новое окно PowerShell и скачайте модель Mistral (~4GB), введя:
ollama pull mistral

5.  Проверьте что модель скачалась, введя:
ollama list

6.  Перейдите в папку с проектом, введя:
cd C:\Местоположение\Ваших\файлов\sparql-generator

7.  Создайте кастомную модель из Modelfile, введя:
ollama create mistral-sparql -f .\Modelfile

8.  Проверьте что модель создана, введя:
ollama list

9.  В папке проекта создайте venv, введя:
python -m venv venv

10.  Активируйте виртуальное окружение, введя:
.\venv\Scripts\Activate.ps1

11.  Установите зависиомсти, введя:
pip install requests

12.  Запустите тест, ввеля:
python sparql_generator.py

13.  введите 2 и создайте запрос
