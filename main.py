import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONFIGURAÇÃO DO DRIVER
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless") # não deixa o terminal visivel quando executar

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

termo = input("O que deseja buscar? ")
url = f"https://www.google.com.br/maps/search/{termo}"
driver.get(url)

wait = WebDriverWait(driver, 10)
lista_links = []
dados_completos = []

# Meta de coleta
META_ITENS = 25 

try:
    print(f"--- FASE 1: Coletando no mínimo {META_ITENS} links ---")
    seletor_link = "a[href*='/maps/place/']"
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_link)))
    
    # Variável de controle para saber se a lista parou de crescer
    qtd_anterior = 0

    #SCROLL DE DADOS
    while True:
        #Pega tudo que já está visível
        elementos = driver.find_elements(By.CSS_SELECTOR, seletor_link)
        qtd_atual = len(elementos)
        
        print(f"Itens carregados: {qtd_atual}...")
        
        #Critério de Parada 1: Meta atingida
        if qtd_atual >= META_ITENS:
            print("Meta atingida!")
            break
        
        #Critério de Parada 2: A lista parou de crescer (Fim dos resultados)
        if qtd_atual == qtd_anterior:
            print("Não há mais itens para carregar. Encerrando scroll.")
            break
        
        # Atualiza a "memória" para a próxima comparação
        qtd_anterior = qtd_atual

        ultimo_item = elementos[-1]
        driver.execute_script("arguments[0].scrollIntoView(true);", ultimo_item)
        
        time.sleep(3) 
        
    
    # Atualiza a lista uma última vez
    elementos = driver.find_elements(By.CSS_SELECTOR, seletor_link)
    
    for el in elementos[:META_ITENS]:
        link = el.get_attribute("href")
        if link:
            lista_links.append(link)
    
    print(f"Links filtrados para processar: {len(lista_links)}")

    print("\n--- FASE 2: Extração Profunda ---")
    
    for i, link in enumerate(lista_links):
        print(f"Extraindo {i+1}/{len(lista_links)}...", end="")
        driver.get(link)
        
        perfil = {
            "Nome": "N/A",
            "Nota": "N/A",
            "Avaliações": "N/A",
            "Telefone": "N/A",
            "Endereço": "N/A",
            "Site": "N/A",
            "Link": link
        }
        
        try:
            #NOME
            try: perfil["Nome"] = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text
            except: pass

            #TELEFONE
            try:
                btn_tel = driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='phone']")
                perfil["Telefone"] = btn_tel.get_attribute("aria-label").replace("Ligar para: ", "")
            except: pass
            
            #SITE
            try:
                btn_site = driver.find_element(By.CSS_SELECTOR, "a[data-item-id*='authority']")
                perfil["Site"] = btn_site.get_attribute("href")
            except: pass

            print(f" -> {perfil['Nome']}")
            
        except Exception as e:
            print(f" [Erro: {e}]")

        dados_completos.append(perfil)
        time.sleep(1) # Respeitando o servidor

except Exception as e:
    print(f"Erro Crítico: {e}")
    driver.save_screenshot("erro_scroll.png")

#SALVANDO
if dados_completos:
    df = pd.DataFrame(dados_completos)
    arquivo = f"lista_top{len(dados_completos)}_{termo.replace(' ', '_')}.xlsx"
    df.to_excel(arquivo, index=False)
    print(f"\nRELATÓRIO GERADO: {arquivo}")
else:
    print("Nenhum dado capturado.")

driver.quit()