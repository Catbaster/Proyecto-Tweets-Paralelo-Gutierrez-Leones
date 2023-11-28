# ÚLTIMO COMMIT de README
Teniendo en cuenta lo aprendido en Sistemas Operativos, los tiempos de lectura y escritura en disco son mucho más altos que los tiempos de carga en RAM, por lo que se puede considerar que en la entrega secuencial lo que ralentizaba más la entrega era la carga de los archivos, la paralelización de la carga de los archivos redujo notablemente el tiempo de ejecución.

# Proyecto-Tweets-Paralelo-Gutierrez-Leones
Se presenta la solución a la paralelización del proyecto secuencial haciendo uso de Message Passing Interface (MPI) con el cual busca se mejorar los tiempos de ejecución al asignar más recursos de procesamiento al proyecto. Cada nodo ejecutará el código de procesamiento "secuencialmente" de forma individual pero paralela por procesos, especifícamente ejecutarán las funciones asociadas a los parámetros que le son entregados mediante el comando de ejecución o mediante el script de verificación encontrado en el proyecto. Con el script de verificación vemos que para esta entrega se trabajó únicamente con los JSON por lo que los JSON correspondientes a la ejecución secuencial y a la ejecución paralela serán generados y se guardarán en la dirección ../testProject con los nombres -json- y -json-p respectivamente. Debe tener en cuenta que el script de verificación puede ser distinto dependiendo de la versión de MPI y de Python instalada en el equipo sobre el que se hará la prueba, leer más en [Acerca del script](https://github.com/Catbaster/Proyecto-Tweets-Paralelo-Gutierrez-Leones/tree/main#acerca-del-script). 

# Consideraciones
1. La paralelización se hizo sobre la entrega secuencial https://github.com/Santimaster13/Proyecto-Tweets-Secuencial-Mercado-Gutierrez-Leones.
2. El código de la entrega paralela se encuentra documentado con los cambios, la gran mayoría de la lógica secuencial se conserva y se modifica principalmente getTweets que es la función que asignará a cada proceso una sublista de archivos con la que deberá trabajar, esta sublista es manejada individualmente por procesos al llamar a process file y finalmente recogerá la información individual para combinarla. La recolección de la información procesada por los demás procesos así como la generación de los grafos y JSON con la información procesada es una tarea única del proceso root.
3. Se instaló Microsoft MPI última versión, Python última versión y Git for Windows última versión, se usó VS code con la extensión de Python.
4. Se requirió, en el proyecto en VS code, con una terminal, ejecutar pip install networkx y pip install mpi4py, posterior a eso la instalación y configuración de Windows Subsystem for Linux (WSL) para intentar ejecutar los scripts directamente desde la terminal de Windows, pero no logramos probar el script desde la terminal de Windows por lo que recurrimos a Git Bash. Eso fue lo que hicimos para ir probando lo que íbamos haciendo.

# Acerca del script
En el proyecto se encuentra un documento en formato .pdf con el que se explica como se llegó a probar el proyecto, para ello fue necesario cambiar el script ligeramente para que corriera sobre el equipo en que se hacían las pruebas, el cambio fue específicamente cambiar mpirun por mpiexec dado que Microsoft MPI implementa dicho comando para la ejecución, además de que la implementación de mpiexec no reconoce --oversubscribe y --allow-run-as-root como parámetros. Puede leer más acerca de esto en el documento info-sobre-script.pdf encontrado en el proyecto, por favor considere esto para poder ejecutar correctamente nuestra entrega, la entrega debe correr sobre el script proporcionado por usted si en su equipo maneja Open MPI o cualquier otra versión de MPI que trabaje con el comando especificado y los parámetros --oversubscribe y --allow-run-as-root, las únicas dependencias fueron networkx y mpi4py.

Con los comandos which mpiexec y which mpirun se puede saber qué comando de mpi es el que debe usarse en el script para la ejecución.

# Cómo ejecutar en este directorio
1. Añadir la información de input en la carpeta de input manteniendo la estructura ..input/año/mes/dia/hora.
2. Eliminar cualquier archivo no deseado como los JSON dentro de ../testProject o la salida testProject.txt estos archivos volverán a generarse o se sobreescribirán.
3. En la carpeta algunosArchivos se encuentran los scripts de verificación usados para las pruebas, verify8.sh y verify-all-nosec.sh usan mpiexec para la ejecución (pueden ser modificados por mpirun si es requerido), verify8.sh prueba el proyecto con 8 procesos, verify-all-nosec.sh hace todas las pruebas menos la secuencial, verifympirun.sh es el script original que usa mpirun.
4. Habiendo elegido el script adecuado o habiéndolo modificado según la información en Acerca del script, se ejecuta en un command prompt o en un bash provider como GNU Bash o Git Bash. En nuestro caso las pruebas se hacían usando Git Bash.
5. Al finalizar la ejecución, el archivo testProject.txt ubicado en la carpeta raíz mostrará las salidas en segundos. Los JSON o grafos (si son enviados como parámetros) se ubicarán en testProject, tanto de entrega secuencial como entrega paralela.

# Cómo ejecutar únicamente con los generadores en directorio de prueba o evaluación
1. Tomar generador.py y generadorp.py y copiarlos sobre la carpeta de prueba que mantenga la misma estructura de input. Los archivos deben ubicarse en una carpeta llamada testProject.
2. Ejecutar con un script acorde a la instalación de MPI y Python del equipo sobre el que se hará la prueba.

# Comentarios
Espero que le parezca bueno nuestro proyecto, se investigó bastante, en un momento estuvimos atascados porque no lográbamos probarlo por los problemas con el script, agradecimientos especiales a StackOverFlow que nos permitió darnos cuenta de las cosas que estábamos haciendo mal, se dedicó tiempo a entender la parte más compleja de la entrega secuencial, parte de la que se encargó nuestro compañero Santiago Mercado, y a usted por poner a nuestra disposición la plantilla de MPI con la que pudimos darnos cuenta más o menos de cómo debíamos implementar MPI en la entrega secuencial y por permitirnos entregar el trabajo aunque haya surgido ese inconveniente con la cuestión de la división del trabajo.

Lo que sí no pudimos hacer fue probar esto con la imagen que usted me decía, eso no se pudo y bueno, hará falta tiempo para poder aprender a manejar docker, gracias por presentarlo para ver las virtudes de ese sistema.
