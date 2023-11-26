import json
import networkx as nx
import os
import sys
import argparse
import time
from datetime import datetime
import bz2
from itertools import combinations
# importar mpi4py que debería funcionar sobre python3 aunque el proyecto haya sido desarrollado e implementado
# para python3.12
from mpi4py import MPI

def get_tweets_parallel_mpi(path, fecha_inicial, fecha_final, hashtags):
    # inicialización de MPI siguiendo la estructura de generadorp.py del proyecto template
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # todos los procesos generan la lista de archivos, pero cada proceso va a procesar sólo una parte
    file_paths = [os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files if file.endswith(".json.bz2")]

    # dividir la lista de archivos entre los procesos
    chunks = [file_paths[i::size] for i in range(size)]
    local_file_paths = chunks[rank]

    # procesar sólo los archivos asignados a este proceso
    local_tweets = [process_file(fp, fecha_inicial, fecha_final, hashtags) for fp in local_file_paths]

    # recolectar todos los tweets procesados de todos los procesos
    all_tweets = comm.gather(local_tweets, root=0)

    # combinar los resultados en el root proceso 0
    if rank == 0:
        tweets = [tweet for sublist in all_tweets for local_list in sublist for tweet in local_list]
        return tweets
    else:
        return None


def process_file(file_path, fecha_inicial, fecha_final, hashtags):
    # procesamiento de archivos asignados
    tweets = []
    if file_path.endswith(".json.bz2"):
        with bz2.BZ2File(file_path, "r") as f:
            for line in f:
                try:
                    if line.strip():
                        tweet = json.loads(line)
                        if "created_at" in tweet and is_tweet_in_range(tweet, fecha_inicial, fecha_final, hashtags):
                            tweets.append(tweet)
                except (UnicodeDecodeError, json.decoder.JSONDecodeError) as e:
                    print(f"Ha ocurrido un error al procesar el archivo {file_path}: {e}")
    return tweets

def is_tweet_in_range(tweet, fecha_inicial, fecha_final, hashtags):
    # si existen filtros ya sea por rango de fechas o por hashtags
    tweet_created_at = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S %z %Y")
    if fecha_inicial.date() <= tweet_created_at.date() <= fecha_final.date():
        if hashtags:
            hashtexts = {hashtag["text"].lower() for hashtag in tweet["entities"]["hashtags"]}
            return bool(hashtexts & hashtags)
        return True
    return False

def worker_process(file_path, fecha_inicial, fecha_final, hashtags):
    return process_file(file_path, fecha_inicial, fecha_final, hashtags)

# Crear los grafos y JSON
def crear_grafo_retweets(tweets):
    grafo = nx.DiGraph()  # Utilizamos un grafo dirigido para representar retweets

    for tweet in tweets:
        if 'user' in tweet:
            user_screen_name = tweet["user"]["screen_name"]
            if "retweeted_status" in tweet and user_screen_name != "null":
              original_tweet = tweet["retweeted_status"]
              original_user_screen_name = original_tweet["user"]["screen_name"]
              if original_user_screen_name != "null":
                if original_user_screen_name not in grafo:
                    grafo.add_node(original_user_screen_name) 
                if user_screen_name not in grafo:
                    grafo.add_node(user_screen_name) 
                # Comprobamos si la arista ya existe entre estos usuarios
                if grafo.has_edge(user_screen_name, original_user_screen_name):
                    grafo[user_screen_name][original_user_screen_name]["weight"] += 1
                else:
                    grafo.add_edge(user_screen_name, original_user_screen_name, weight=1)

    return grafo


def crear_json_retweets(tweets):
    result = {}
    elements = []
    guide = {}
    ind = 0
    for tweet in tweets:
        if 'user' in tweet:
            user_screen_name = tweet["user"]["screen_name"]

            if "retweeted_status" in tweet and user_screen_name != "null":
               original_tweet = tweet["retweeted_status"]
               original_user_screen_name = original_tweet["user"]["screen_name"]
               if original_user_screen_name != "null":
                if original_user_screen_name not in result:
                    result[original_user_screen_name] = {
                        'username' : original_user_screen_name, 
                        "receivedRetweets": 0,
                        "tweets": {}
                    }
                    guide[original_user_screen_name] = ind
                    ind = ind + 1
                    elements.append(result[original_user_screen_name])
                original_tweet_id = "tweetId: " + original_tweet["id_str"]

                if original_tweet_id not in result[original_user_screen_name]["tweets"]:
                    result[original_user_screen_name]["tweets"][original_tweet_id] = {
                        "retweetedBy": []
                    }
                    elements[guide[original_user_screen_name]] = result[original_user_screen_name] 
                if user_screen_name not in result[original_user_screen_name]["tweets"][original_tweet_id]["retweetedBy"]:
                    result[original_user_screen_name]["tweets"][original_tweet_id]["retweetedBy"].append(user_screen_name)
                    result[original_user_screen_name]["receivedRetweets"] += 1
                    elements[guide[original_user_screen_name]] = result[original_user_screen_name] 
    # Ordenar el JSON por número total de retweets de mayor a menor
    sorted_list = sorted(elements, key=lambda x: x['receivedRetweets'], reverse=True)
    result2 = {'retweets': sorted_list}
    return result2



def crear_json_menciones(tweets):
    result = {}
    elements = []
    guide = {}
    ind = 0
    for tweet in tweets:
        if 'user' in tweet:
          if "retweeted_status" not in tweet and tweet["user"]["screen_name"] != "null": 
                user_screen_name = tweet["user"]["screen_name"]
                mentioned_users = [mencion["screen_name"] for mencion in tweet.get("entities", {}).get("user_mentions", [])]
                repeats = {}
                for mentioned_user in mentioned_users:
                  if mentioned_user not in repeats and mentioned_user != "null": 
                    repeats[mentioned_user] = 1
                    if mentioned_user not in result:
                        result[mentioned_user] = {
                        "username": mentioned_user,
                        "receivedMentions": 0,
                        "mentions": []
                        }
                        guide[mentioned_user] = {'index': ind, 'mentioners': {}}
                        ind = ind + 1
                        elements.append(result[mentioned_user])
                    if user_screen_name not in guide[mentioned_user]['mentioners']:
                        result[mentioned_user]['mentions'].append({
                            "mentionBy": user_screen_name,
                            "tweets": []
                        })
                        guide[mentioned_user]['mentioners'][user_screen_name] = len(result[mentioned_user]['mentions']) - 1 
                        result[mentioned_user]["mentions"][guide[mentioned_user]['mentioners'][user_screen_name]]["tweets"].append(tweet["id_str"])
                    else:
                        result[mentioned_user]["mentions"][guide[mentioned_user]['mentioners'][user_screen_name]]["tweets"].append(tweet["id_str"])
                    result[mentioned_user]["receivedMentions"] += 1
                    elements[guide[mentioned_user]['index']] = result[mentioned_user] 

    # Ordenar el JSON por número de menciones de mayor a menor
    sorted_list = sorted(elements, key=lambda x: x['receivedMentions'], reverse=True)
    result2 = {'mentions': sorted_list}
    return result2

def crear_grafo_menciones(tweets):
    grafo = nx.DiGraph() 

    for tweet in tweets:
        if 'user' in tweet:
          if "retweeted_status" not in tweet and tweet["user"]["screen_name"] != "null":  # Verificar que no sea un retweet
            user_screen_name = tweet["user"]["screen_name"]
            mentioned_users = [mencion["screen_name"] for mencion in tweet.get("entities", {}).get("user_mentions", [])]
            repeats = {}
            if user_screen_name not in grafo:
                grafo.add_node(user_screen_name)

            for mentioned_user in mentioned_users:
              if mentioned_user not in repeats and mentioned_user != "null": 
                repeats[mentioned_user] = 1
                if mentioned_user not in grafo:
                    grafo.add_node(mentioned_user)

                # Comprobamos si la arista ya existe entre estos usuarios
                if grafo.has_edge(user_screen_name, mentioned_user):
                    grafo[user_screen_name][mentioned_user]["weight"] += 1
                else:
                    grafo.add_edge(user_screen_name, mentioned_user, weight=1)

    return grafo


def crear_json_coretweets(tweets):
    retweet_dict = {} 
    elements = []
    guide = {}
    ind = 0
    for tweet in tweets:
        retweeter = tweet['user']['screen_name']

        # Comprobar si el tweet es un retweet
        if 'retweeted_status' in tweet and 'user' in tweet:
          author = tweet['retweeted_status']['user']['screen_name']
          if author != retweeter and author != "null" and retweeter != "null":
            # Actualizar el diccionario de retweets
            if retweeter not in retweet_dict and author:
                retweet_dict[retweeter] = []
            retweet_dict[retweeter].append(author) 
    result = {}  
    for clave, lista in retweet_dict.items():
        elementos_vistos = []
        for elemento in lista:
            if elemento not in elementos_vistos:
                if elemento != clave:
                    elementos_vistos.append(elemento)
        # Almacenar el par en el diccionario de pares iguales
        combinaciones = combinations(elementos_vistos, 2)
        for combo in combinaciones:
            parautores = f"authors: {[combo[0], combo[1]]}"
            parautores2 = f"authors: {[combo[1], combo[0]]}"
            if parautores not in result and parautores2 not in result:
                result[parautores] = {
                    'authors':{'u1': combo[0], 'u2': combo[1]},
                    'totalCoretweets': 0,
                    'retweeters': [] 
                }
                result[parautores]['retweeters'].append(clave)
                result[parautores]['totalCoretweets'] += 1
                guide[parautores] = ind
                ind = ind + 1
                elements.append(result[parautores])
            elif parautores in result and parautores2 not in result:
                if clave not in result[parautores]['retweeters']:
                    result[parautores]['retweeters'].append(clave)
                    result[parautores]['totalCoretweets'] += 1
                    elements[guide[parautores]] = result[parautores] 
            elif parautores2 in result and parautores not in result:
                if clave not in result[parautores2]['retweeters']:
                    result[parautores2]['retweeters'].append(clave)
                    result[parautores2]['totalCoretweets'] += 1
                    elements[guide[parautores2]] = result[parautores2] 
    sorted_list = sorted(elements, key=lambda x: x['totalCoretweets'], reverse=True)
    result2 = {'coretweets': sorted_list}
    return result2

def crear_grafo_coretweets(tweets):
    grafo = nx.Graph() 
    retweet_dict = {}  
    for tweet in tweets:
        retweeter = tweet['user']['screen_name']  

        # Comprobar si el tweet es un retweet
        if 'retweeted_status' in tweet and 'user' in tweet:
          author = tweet['retweeted_status']['user']['screen_name']
          if author != retweeter and author != "null" and retweeter != "null":
            # Actualizar el diccionario de retweets
            if retweeter not in retweet_dict and author:
                retweet_dict[retweeter] = []
            retweet_dict[retweeter].append(author) 
    result = {}  
    for clave, lista in retweet_dict.items():
        elementos_vistos = []
        for elemento in lista:
            if elemento not in elementos_vistos:
                if elemento != clave:
                    elementos_vistos.append(elemento)
        # Almacenar el par en el diccionario de pares iguales
        combinaciones = combinations(elementos_vistos, 2)
        for combo in combinaciones:
            parautores = f"authors: {[combo[0], combo[1]]}"
            parautores2 = f"authors: {[combo[1], combo[0]]}"
            if parautores not in result and parautores2 not in result:
                if combo[0] not in grafo:
                    grafo.add_node(combo[0])
                if combo[1] not in grafo:
                    grafo.add_node(combo[1])
                if grafo.has_edge(combo[0], combo[1]): #En teoria no se deberia dar nunca pero por si acaso
                    grafo[combo[0]][combo[1]]["weight"] += 1
                else: 
                    grafo.add_edge(combo[0], combo[1], weight=1)
                result[parautores] = {
                    'retweeters': [] 
                }
                result[parautores]['retweeters'].append(clave)
            elif parautores in result and parautores2 not in result:
                    if clave not in result[parautores]['retweeters']:
                        result[parautores]['retweeters'].append(clave)
                        if grafo.has_edge(combo[0], combo[1]): 
                            grafo[combo[0]][combo[1]]["weight"] += 1
                        else: 
                            grafo.add_edge(combo[0], combo[1], weight=1)
            elif parautores2 in result and parautores not in result:
                    if clave not in result[parautores2]['retweeters']:
                        result[parautores2]['retweeters'].append(clave)
                        if grafo.has_edge(combo[1], combo[0]): 
                            grafo[combo[1]][combo[0]]["weight"] += 1
                        else: 
                            grafo.add_edge(combo[1], combo[0], weight=1)

    return grafo



def imprimir_resultados(grafo, salida):
    if salida.endswith(".gexf"):
        nx.write_gexf(grafo, salida)
    elif salida.endswith(".json"):
        with open(salida, "w") as f:
            json.dump(list(grafo.nodes(data=True)), f, indent=4) 

def parse_args(argv):
    parser = argparse.ArgumentParser(description="Argumentos para generador.py", add_help=False)
    parser.add_argument("-d", "--directory", default="data", help="Ruta al directorio de datos")
    parser.add_argument("-fi", "--fecha-inicial", help="Fecha inicial")
    parser.add_argument("-ff", "--fecha-final", help="Fecha final")
    parser.add_argument("-h", "--hashtags", help="Lista de hashtags")
    parser.add_argument("-grt", action="store_true", help="Crear grafo de retweets")
    parser.add_argument("-jrt", action="store_true", help="Crear JSON de retweets")
    parser.add_argument("-gm", action="store_true", help="Crear grafo de menciones")
    parser.add_argument("-jm", action="store_true", help="Crear JSON de menciones")
    parser.add_argument("-gcrt", action="store_true", help="Crear grafo de corretweets")
    parser.add_argument("-jcrt", action="store_true", help="Crear JSON de corretweets")
    args = parser.parse_args(argv)
    args = vars(args)
    if "directory" not in args:
       args["directory"] = "data"
    return args

def main():
    # inicialización de MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    start_time = time.time()
    
    args = parse_args(sys.argv[1:])
    fecha_inicial = datetime.strptime("01-01-16", "%d-%m-%y")
    fecha_final =   datetime.strptime("01-01-24", "%d-%m-%y")

    if args["fecha_inicial"]:
        fecha_inicial = datetime.strptime(args["fecha_inicial"], "%d-%m-%y")
        

    if args["fecha_final"]:
        fecha_final = datetime.strptime(args["fecha_final"], "%d-%m-%y")

    hashtagsl = []
    if args["hashtags"]:
        with open(args["hashtags"], 'r') as archivo:
            hashtagsl = {line.strip().lower().lstrip("#") for line in archivo.readlines()}

    tweets = get_tweets_parallel_mpi(args["directory"], fecha_inicial, fecha_final, hashtagsl)

    ruta_base = os.getenv('RUTA_ARCHIVOS_SALIDA', '')

    # si se encuentra en el proceso raíz y aceptando todos los parámetros de la entrega (los parámetros en el script)
    # creará los grafos y JSON respectivos con la información ya recolectada,
    # este procedimiento es hecho únicamente por el proceso raíz,
    # los demás procesos se encargan del procesamiento pero no de la construcción de los archivos
    if rank == 0:

        if args["grt"]:
            grafo = crear_grafo_retweets(tweets)
            imprimir_resultados(grafo, os.path.join(ruta_base, "rtp.gexf"))
        if args["jrt"]:
            json_retweets = crear_json_retweets(tweets)
            with open(os.path.join(ruta_base, "rtp.json"), "w") as f:
                json.dump(json_retweets, f, indent=4)  
        if args["gm"]:
            grafo = crear_grafo_menciones(tweets)
            imprimir_resultados(grafo, os.path.join(ruta_base, "mencionp.gexf"))
        if args["jm"]: 
            json_menciones = crear_json_menciones(tweets)
            with open(os.path.join(ruta_base, "mencionp.json"), "w") as f:
                json.dump(json_menciones, f, indent=4)
        if args["gcrt"]:
            grafo = crear_grafo_coretweets(tweets)
            imprimir_resultados(grafo, os.path.join(ruta_base, "corrtwp.gexf"))
        if args["jcrt"]:
            json_corretweets = crear_json_coretweets(tweets)
            with open(os.path.join(ruta_base, "corrtwp.json"), "w") as f:
                json.dump(json_corretweets, f, indent=4)
        print(time.time() - start_time)
    

if __name__ == "__main__":
    main()
