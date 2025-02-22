from flask import Flask, request, jsonify
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

app = Flask(__name__)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Inicializa o navegador
def iniciar_navegador():
    navegador = webdriver.Chrome()
    navegador.get("https://jcrisco.com.br/logtrack/index.php#")
    navegador.maximize_window()
    return navegador

# Login
def realizar_login(navegador):
    try:
        usuario = navegador.find_element(By.CSS_SELECTOR, ".textbox-text.validatebox-text.textbox-prompt.validatebox-invalid")
        usuario.send_keys(55032620858)

        senha = navegador.find_element(By.CSS_SELECTOR, "input[type='password'].textbox-text.validatebox-text")
        senha.send_keys(280406)

        botao_entrar = navegador.find_element(By.ID, "btnEntrar")
        botao_entrar.click()
        time.sleep(3)
        return "Login realizado com sucesso!"
    except Exception as e:
        return f"Erro ao tentar realizar login: {e}"

# Acessando Configurações e Clientes
def acessar_clientes(navegador):
    try:
        elemento_configuracoes = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Configurações']"))
        )
        elemento_configuracoes.click()
        time.sleep(2)

        elemento_cliente = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='menu-text' and text()='Clientes']"))
        )
        elemento_cliente.click()
        return "Acessado clientes com sucesso!"
    except Exception as e:
        return f"Erro ao acessar clientes: {e}"

# Selecionando a quantidade de clientes
def selecionar_clientes(navegador):
    try:
        select_element = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pagination-page-list"))
        )
        select = Select(select_element)
        select.select_by_visible_text("1000")
        time.sleep(2)
        return "Clientes selecionados com sucesso!"
    except Exception as e:
        return f"Erro ao selecionar clientes: {e}"

# Função de rolagem até encontrar o nome
def rolar_ate_encontrar(navegador, nome, timeout=20):
    tempo_inicial = time.time()
    while time.time() - tempo_inicial < timeout:
        try:
            linhas = navegador.find_elements(By.XPATH, f"//tr[td/div[contains(text(), '{nome}')]]")
            if linhas:
                linhas[0].click()
                time.sleep(2)
                return f"Cliente {nome} encontrado e selecionado!"
            navegador.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.5)
        except Exception as e:
            return f"Erro ao rolar até encontrar o nome {nome}: {e}"
    navegador.execute_script("window.scrollTo(0, 0);")
    return f"Nome {nome} não encontrado dentro do tempo."

# Esperar e clicar em elementos via WebDriver
def esperar_e_clicar_elemento(navegador, by, value, timeout=10):
    try:
        elemento = WebDriverWait(navegador, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        elemento.click()
        time.sleep(2)
        return f"Elemento {value} clicado com sucesso!"
    except Exception as e:
        return f"Erro ao tentar clicar no elemento {value}: {e}"

# Selecionar a fonte (checkbox e dropdown)
def selecionar_fonte(navegador):
    try:
        checkbox = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="frmCadastroClienteOperacaoTransportador"]/label[1]/span/input[1]'))
        )
        checkbox.click()

        JC_element = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[32]/div/div[1]'))
        )
        JC_element.click()
        time.sleep(2)
        JC_element.click()
        return "Fonte selecionada com sucesso!"
    except Exception as e:
        return f"Erro ao tentar selecionar a fonte: {e}"

@app.route('/sprisk', methods=['POST'])
def processo_principal():
    navegador = iniciar_navegador()
    login_status = realizar_login(navegador)
    if "Erro" in login_status:
        return jsonify({"status": login_status})

    acessar_status = acessar_clientes(navegador)
    if "Erro" in acessar_status:
        return jsonify({"status": acessar_status})

    selecionar_status = selecionar_clientes(navegador)
    if "Erro" in selecionar_status:
        return jsonify({"status": selecionar_status})

    nomes = request.json.get('nomes', ["1A99", "ALPHA EXPRESS", "ARTICO", "ASUS", "AVIAT", "AVILOG", "BASF", "BR4", "COLUMBIA", "DIRECT",
             "DOMINALOG", "ECO EXPRESS", "ECOPORTO", "ENIVIX", "ESSEMAGA", "ESTRELA DOURADA", "FATELOG", "FIORDE",
             "FORTE MINAS", "GAB TRANSPORTES", "GELOG", "GH NEVES", "GMM TRANSPORTES", "GOLDEN CARGO", "HOPE LINGERIE",
             "HYPERA", "IBRAM", "JOPAL TRANSPORTES", "MAGNUM", "MARIMEX", "MERCK SHARP", "NEXANS", "NOVELIS", "NOVO NORDISK",
             "PANTHERS", "PHL", "PLATINUM LOG", "ROBERT BOSCH", "ROCHE", "RODOLUKI", "RODOPRIME", "ROUTE/PENHA", "SAFELAB",
             "SCALT", "SERRAVIX", "SHLOG", "SOFTRONIC", "SOMERLOG", "STEFANIN", "TANGERINA", "TOLIMAN", "TRANSLAG",
             "TRANSLEG", "UNIPAR", "VITA SANO", "WILSON SONS"])
    for nome in nomes:
        rolar_status = rolar_ate_encontrar(navegador, nome)
        if "Erro" in rolar_status:
            return jsonify({"status": rolar_status})

        editar_status = esperar_e_clicar_elemento(navegador, By.ID, "btnEditarCliente")
        if "Erro" in editar_status:
            return jsonify({"status": editar_status})

        dados_status = esperar_e_clicar_elemento(navegador, By.XPATH, "//span[text()='Dados Cliente']")
        if "Erro" in dados_status:
            return jsonify({"status": dados_status})

        fonte_status = selecionar_fonte(navegador)
        if "Erro" in fonte_status:
            return jsonify({"status": fonte_status})

        gravar_status = esperar_e_clicar_elemento(navegador, By.XPATH, "//*[@id='btnClienteOperacaoTransportadorGravar']")
        if "Erro" in gravar_status:
            return jsonify({"status": gravar_status})

        navegador.refresh()
        time.sleep(3)
        acessar_clientes(navegador)
        selecionar_clientes(navegador)

    navegador.quit()
    return jsonify({"status": "Processo concluído com sucesso!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
