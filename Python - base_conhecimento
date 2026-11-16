import json
import os
from orientacao import Orientacao

ACENTOS = {
    "á": "a", "à": "a", "ã": "a", "â": "a",
    "é": "e", "ê": "e",
    "í": "i",
    "ó": "o", "õ": "o", "ô": "o",
    "ú": "u", "ü": "u",
    "ç": "c"
}

def normalizar(texto):
    texto = str(texto).lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()[]{}'\"-":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        self.orientacoes = []
        if not os.path.exists(self.caminho):
            print(f"[ERRO] Arquivo '{self.caminho}' não encontrado.")
            return False

        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)

            if not isinstance(dados, list):
                print("[ERRO] Formato inválido no JSON. Esperada uma lista de registros.")
                return False

            for item in dados:
                ori = Orientacao(
                    id_orientacao=item["id"],
                    categoria=item["categoria"],
                    titulo=item["titulo"],
                    palavras_chave=item["palavras_chave"],
                    resposta=item["resposta"],
                    documentos=item["documentos"],
                    onde=item["onde"],
                    fonte=item["fonte"],
                    verificado_em=item["verificado_em"]
                )
                self.orientacoes.append(ori)
            return True

        except json.JSONDecodeError:
            print(f"[ERRO] O arquivo '{self.caminho}' está corrompido (JSON inválido).")
            return False
        except KeyError as e:
            print(f"[ERRO] Campo obrigatório ausente no JSON: {e}")
            return False
        except Exception as e:
            print(f"[ERRO] Falha inesperada ao ler a base: {e}")
            return False

    def categorias(self):
        cats = sorted(list(set(o.categoria for o in self.orientacoes)))
        return cats

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pontos = 0
        pergunta_norm = normalizar(pergunta)

        # +3 pontos por palavra-chave que aparece na pergunta
        for kw in orientacao.palavras_chave:
            kw_norm = normalizar(kw).strip()
            if kw_norm and f" {kw_norm} " in pergunta_norm:
                pontos += 3

        # +1 ponto por palavra da pergunta (4+ letras) que aparece no título
        titulo_norm = normalizar(orientacao.titulo)
        palavras_pergunta = set(pergunta_norm.strip().split())
        for palavra in palavras_pergunta:
            if len(palavra) >= 4 and f" {palavra} " in titulo_norm:
                pontos += 1

        return pontos

    def buscar(self, pergunta):
        resultados = []
        for ori in self.orientacoes:
            pts = self.pontuar(pergunta, ori)
            if pts > 0:
                resultados.append((pts, ori))

        # Ordena da maior para a menor pontuação
        resultados.sort(key=lambda x: x[0], reverse=True)
        return resultados
