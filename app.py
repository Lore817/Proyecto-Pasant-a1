from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import csv
import os

import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
PLANILLA_FOLDER= 'subir_datos'
app.config[ 'UPLOAD_FOLDER'] = PLANILLA_FOLDER

#configuracion de la base de datos.
bd = pymysql.connect(
    host='localhost',
    user= 'root',
    database= ' gestion_correos'
)


@app.route('/')
def index():
    return render_template('subir_datos.html')

@app.route('/subir_datos', methods=['POST'])
def subir_datos():
    if 'file' not in request.files:
        flash('No se encontro el archivo.')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename =='':
        flash('Nombre de archivo vacio.')
        return redirect('request.url')
    
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['PLANILLA_FOLDER'], file.filename)
        file.save(filepath)

        with open(filepath, newline= '', encoding='utf8') as csvfile:
            lector = csv.DictReader(csvfile)
            cursor = bd.cursor()

        for fila in lector:
            nombre = fila['nombre_apellido']
            correo = fila ['correo']
            tipo_licencia = fila['tipo_licencia']
            fecha = fila['feche_creacion']
    
        # busca si ya existe el usurio 
            
            cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s",(correo,))
            usuario = cursor.fetchone()

            if usuario:
                id_usuario = usuario[0]
                #actualiza los datos
                cursor.execute("""
                INSERT INTRO usuario (nombre_apellido, correo, tipo_licencia, fecha_creacion)
                VALUES (%s, %s, %s)
                
                """, (nombre, correo, fecha))
                id_usuario = cursor.lastrowid
             #obtiene id de la licencia

            cursor.execute("SELECT id_licencia FROM lincencias WHERE tipo_licencia =%s",(tipo_licencia,))
            licencia = cursor.fetchone()
            if licencia:
                id_licencia = licencia [0]
                #verifica relacion
            cursor.execute("""SELECT id_licencia_usuario FROM licencia_usuario WHERE id_usuario=$s           
            """,(id_usuario,))
            rel = cursor.fetchone()

            if rel:

                #actuliza relacion
                cursor.execute("""UPDATE licencia_usuario SET id_licencia =%s, fecha_creacion =%s, registro_cambio =$s 
                               WHERE id_usuario =%s """,(id_licencia, fecha, 'Actualizacion de CSV', id_usuario))
            else: #insertar nueva relacion 
                cursor.execute("""INSERT INTO licencia_usuario(id_usuario, id_licencia, fecha_creacion, registro_cambio)
                    VALUES (%s, %s, %s)"""
                ,(id_usuario, id_licencia, fecha, 'Carga Inicial'))

#         db.commit()
#         cursor.close()
#         flash('CSV procesando correctamente.')
#         return redirect('/usuarios')
#     else:
#         flash('Archivo no válido. Solo CSV.')
#         return redirect('/')
    

# @app.route('/usuarios')
# def moostrar_usuarios():
#     cursor =db.cursor(pymysql.cursors.DictCursor)
#     cursor.execute("""SELECT u.id_usuario, u.nombre_apellido, u.correo, u.fecha_creacion, l.tipo_licencia, l.costo_mensual
#                    FROM usuario u 
#                    LEFT JOIN licencia_usuario lu ON u.id_usuario = lu. id_usuario
#                    LEFT JOIN licencias l ON lu.id_licencia = l.id_licencia""") 
#     datos = cursor.fetchall()
#     cursor.close()
#     return render_template('usuario.html', usuarios =datos)
# if __name__== '__main__':
#     app.run(debug=True)
