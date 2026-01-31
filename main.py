import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do driver do chrome 
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

#forma de conseguir "burlar" o find element por id etc...

termo = input("O que você quer buscar? ")
url = f"https://www.google.com.br/maps/search/{termo}"
print(f"Acessando: {url}")
driver.get(url)

#configuração do wait para não cair em casos em que a pagina não terminou de carrefar
wait = WebDriverWait(driver, 10)

try:
    print("Carregando resultados...")
    #parte mais "importante" é a configuração da estrutura html para os dados que abrem na lateral (normalmente agrupados)
    seletor = "a[href*='/maps/place/']"
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor)))
    elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
    
    #cria uma "estrutura" dos dado lidos
    for i, el in enumerate(elementos):
        
        nome = el.get_attribute("aria-label")
        link = el.get_attribute("href")

        if nome:
            print(f"{i+1}. {nome}")
            
#caso apresente algum problema tira print
except Exception as e:
    driver.save_screenshot("erro_extracao.png")

print("Fim extracao")
time.sleep(5)
driver.quit()