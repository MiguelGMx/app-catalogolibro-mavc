from os import pipe
from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

from sqlalchemy.sql.elements import Null

#---------------------------------  Conexion Base de datos 
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1205@localhost:5432/db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://onppjfopaaxjta:00dee83c68dc4fa883bb2f7a1149ba2afff80f744e6aaddbcf3d32b7cfdbc79a@ec2-18-211-185-154.compute-1.amazonaws.com:5432/dc9v507bsqlkrd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#----------------------------------------  Tabla Usuarios 
class Usuarios(db.Model):
	__tablename__ = "usuarios"

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(80))
	password = db.Column(db.String(255))

	def __init__(self, email, password):
		self.email=email
		self.password=password

#----------------------------------------  Tabla Editorial 
class Editorial(db.Model):
	__tablename__ = "editorial"
	id_editorial = db.Column(db.Integer, primary_key = True)
	nombre_editorial = db.Column(db.String(80))

	def __init__(self, nombre_editorial):
		self.nombre_editorial=nombre_editorial

#----------------------------------------  Tabla Autor 
class Autor(db.Model):
	__tablename__ = "autor"
	id_autor = db.Column(db.Integer, primary_key = True)
	nombre_autor = db.Column(db.String(80))
	fecha_nacimiento = db.Column(db.Date)
	nacionalidad = db.Column(db.String(30))

	def __init__(self, nombre_autor, fecha_nacimiento, nacionalidad):
		self.nombre_autor = nombre_autor
		self.fecha_nacimiento = fecha_nacimiento
		self.nacionalidad = nacionalidad

#----------------------------------------  Tabla Genero 
class Genero(db.Model):
	__tablename__ = "genero"
	id_genero = db.Column(db.Integer, primary_key = True)
	tipo_genero = db.Column(db.String(80))

	def __init__(self, tipo_genero):
		self.tipo_genero = tipo_genero

#----------------------------------------  Tabla Libros 
class Libro(db.Model):
	__tablename__ = "libro"
	id_libro = db.Column(db.Integer, primary_key = True)
	nombre_libro = db.Column(db.String(80))
	fecha_publicacion = db.Column(db.Date)
	numero_paginas = db.Column(db.Integer)
	formato = db.Column(db.String(30))
	volumen = db.Column(db.Integer)
	resumen = db.Column(db.String(1000))
	link = db.Column(db.String(300))
	#Relacion
	id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
	id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))
	id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))

	def __init__(self, nombre_libro, fecha_publicacion, numero_paginas, formato, volumen, resumen, link, id_editorial, id_autor, id_genero):
		self.nombre_libro = nombre_libro
		self.fecha_publicacion = fecha_publicacion
		self.numero_paginas = numero_paginas
		self.formato = formato
		self.volumen = volumen
		self.resumen = resumen
		self.link = link
		self.id_editorial = id_editorial
		self.id_autor = id_autor
		self.id_genero = id_genero

#----------------------------------------  Tabla MisFavoritos 
class MisFavoritos(db.Model):
	id_favorito = db.Column(db.Integer, primary_key = True)
	#Relacion
	id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))
	id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

	def __init__(self, id_libro, id_usuario):
		self.id_libro = id_libro
		self.id_usuario = id_usuario

#----------------------------------------  Login 
@app.route("/")
def index():
	return render_template("index.html")

#---------------------------------------- Menu
@app.route("/menu")
def menu():
	libros = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Libro.link,Libro.nombre_libro,Autor.nombre_autor,Autor.nacionalidad,Libro.fecha_publicacion,Genero.tipo_genero,Editorial.nombre_editorial,Libro.numero_paginas,Libro.formato,Libro.volumen,Libro.resumen,Libro.id_libro)
	#consulta_libro = Libro.query.all()
	#for libro in consulta_libro:
	#	obj_autor = Autor.query.filter_by(id_autor=libro.id_autor).first()
	#	libro.nombre_autor = obj_autor.nombre_autor
	#	libro.nacionalidad = obj_autor.nacionalidad
	#	obj_editorial = Editorial.query.filter_by(id_editorial=libro.id_editorial).first()
	#	libro.nombre_editorial = obj_editorial.nombre_editorial
	#	obj_genero = Genero.query.filter_by(id_genero=libro.id_genero).first()
	#	libro.tipo_genero = obj_genero.tipo_genero
	return render_template("menu.html", consulta_libro=libros)

#----------------------------------------  Logearse 
@app.route("/login", methods=["POST"])
def login():
	email = request.form["email"]
	password = request.form["password"]
	consultar_usuarios = Usuarios.query.filter_by(email=email).first()
	bcrypt.check_password_hash(consultar_usuarios.password,password)
	
	consulta_libro = Libro.query.all()
	for libro in consulta_libro:
		obj_autor = Autor.query.filter_by(id_autor=libro.id_autor).first()
		libro.nombre_autor = obj_autor.nombre_autor
		libro.nacionalidad = obj_autor.nacionalidad
		obj_editorial = Editorial.query.filter_by(id_editorial=libro.id_editorial).first()
		libro.nombre_editorial = obj_editorial.nombre_editorial
		obj_genero = Genero.query.filter_by(id_genero=libro.id_genero).first()
		libro.tipo_genero = obj_genero.tipo_genero

	resp = make_response(render_template("menu.html", consulta_libro=consulta_libro))
	resp.set_cookie('userID', str(consultar_usuarios.id))

	return resp

#---------------------------------------- Cerrar sesion
@app.route("/cerrar")
def cerrar():
	resp = make_response(redirect("/"))
	resp.delete_cookie("userID")
	return resp

#---------------------------------------- Agregar un favorito
@app.route("/addfavorito/<id>")
def addfavorito(id):
	userid = request.cookies.get('userID')
	userid = int(userid)
	
	mifav = MisFavoritos.query.filter_by(id_libro = int(id), id_usuario=userid).first()
	if mifav == None:
		misfavoritos = MisFavoritos(id_libro=id,id_usuario=userid)
		db.session.add(misfavoritos)
		db.session.commit()

	return redirect("/menu")

#---------------------------------------- Eliminar un favorito
@app.route("/elimifavorito/<id>")
def elimifavorito(id):
	mifav = MisFavoritos.query.filter_by(id_favorito = int(id)).delete()
	db.session.commit()
	return redirect("/fav")
#----------------------------------------  Redireccion Registrar 
@app.route("/registrar")
def registrar():
	return render_template("registrar.html")

#----------------------------------------  Redireccion MisFavoritos 
@app.route("/fav")
def fav():
	userid = request.cookies.get('userID')
	userid = int(userid)
	mifavorito = MisFavoritos.query.filter_by(id_usuario=userid).join(Libro, MisFavoritos.id_libro == Libro.id_libro).join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Libro.link,Libro.nombre_libro,Autor.nombre_autor,Autor.nacionalidad,Libro.fecha_publicacion,Genero.tipo_genero,Editorial.nombre_editorial,Libro.numero_paginas,Libro.formato,Libro.volumen,Libro.resumen,Libro.id_libro,MisFavoritos.id_favorito)
	#consultafav1 = MisFavoritos.query.filter_by(id_usuario=userid)
	#consultafav = []
	#for j in consultafav1:
	#	consultafav.append(j)
	#for favorito in consultafav:
	#	obj_libro = Libro.query.filter_by(id_libro=favorito.id_libro).first()
	#	favorito.nombre_libro = obj_libro.nombre_libro
	#	favorito.fecha_publicacion = obj_libro.fecha_publicacion
	#	favorito.numero_paginas = obj_libro.numero_paginas
	#	favorito.formato = obj_libro.formato
	#	favorito.volumen = obj_libro.volumen
	#	favorito.resumen = obj_libro.resumen
	#	favorito.link = obj_libro.link
	#	favorito.id_autor = obj_libro.id_autor
	#	favorito.id_editorial = obj_libro.id_editorial
	#	favorito.id_genero = obj_libro.id_genero
	#	obj_autor = Autor.query.filter_by(id_autor=favorito.id_autor).first()
	#	favorito.nombre_autor = obj_autor.nombre_autor
	#	favorito.nacionalidad = obj_autor.nacionalidad
	#	obj_editorial = Editorial.query.filter_by(id_editorial=favorito.id_editorial).first()
	#	favorito.nombre_editorial = obj_editorial.nombre_editorial
	#	obj_genero = Genero.query.filter_by(id_genero=favorito.id_genero).first()
	#	favorito.tipo_genero = obj_genero.tipo_genero
	
	return render_template("misfav.html", consulta_libro=mifavorito)
#----------------------------------------  Registro a Inicio 
@app.route("/iniciar_sesion")
def iniciar_sesion():
	redirect("/")

#----------------------------------------  Registrar Usuario 
@app.route("/registrar_usuario", methods=["POST"])
def registrar_usuario():
	email = request.form["email"]
	password = request.form["password"]
	password_cifrado = bcrypt.generate_password_hash(password).decode('utf-8')

	usuario = Usuarios(email=email, password=password_cifrado)
	db.session.add(usuario)
	db.session.commit()
	return redirect("/")

#----------------------------------------  Registrar Libro
@app.route("/registrar_libro", methods=["POST"])
def registrar_libro():
	nombre_libro = request.form["nombre_libro"]
	fecha_publicacion = request.form["fecha_publicacion"]
	numero_paginas = request.form["numero_paginas"]
	formato = request.form["formato"]
	volumen = request.form["volumen"]
	resumen = request.form["resumen"]
	link = request.form["link"]
	id_editorial = request.form["editorial"]
	id_editorial = int(id_editorial)
	id_autor = request.form["autor"]
	id_autor = int(id_autor)
	id_genero = request.form["genero"]
	id_genero = int(id_genero)
	libro = Libro(nombre_libro=nombre_libro,fecha_publicacion=fecha_publicacion,numero_paginas=numero_paginas,formato=formato,volumen=volumen,resumen=resumen,link=link,id_editorial=id_editorial,id_autor=id_autor,id_genero=id_genero)
	db.session.add(libro)
	db.session.commit()
	return redirect("/libro")
#Ver Libro
@app.route("/verlibro")
def verlibro():
	consulta = Libro.query.all()
	for libro in consulta:
		obj_editorial = Editorial.query.filter_by(id_editorial=libro.id_editorial).first()
		libro.nombre_editorial = obj_editorial.nombre_editorial
		obj_genero = Genero.query.filter_by(id_genero=libro.id_genero).first()
		libro.tipo_genero = obj_genero.tipo_genero
		obj_autor = Autor.query.filter_by(id_autor=libro.id_autor).first()
		libro.nombre_autor = obj_autor.nombre_autor
	return render_template("verlibro.html", consulta = consulta)
#Eliminar Libro
@app.route("/eliminarlibro/<id>")
def eliminarlibro(id):
	Libro.query.filter_by(nombre_libro = id).delete()
	db.session.commit()
	return redirect("/verlibro")
#Ir a modificar Libro
@app.route("/editarlibro/<id>")
def editarlibrover(id):
	nota = Libro.query.filter_by(nombre_libro = id).first()
	consulta_editorial = Editorial.query.all()
	consulta_genero = Genero.query.all()
	consulta_autor = Autor.query.all()
	return render_template("modificarlibro.html", nota = nota, consulta_editorial=consulta_editorial, consulta_genero=consulta_genero, consulta_autor= consulta_autor)
#Modificar Autor
@app.route("/modificarlibro", methods=['POST'])
def modificarlibro():
	id_libro = request.form["id_libro"]
	nombre_libro = request.form["nombre_libro"]
	fecha_publicacion = request.form["fecha_publicacion"]
	numero_paginas = request.form["numero_paginas"]
	formato = request.form["formato"]
	volumen = request.form["volumen"]
	resumen = request.form["resumen"]
	link = request.form["link"]
	id_editorial = request.form["editorial"]
	id_autor = request.form["autor"]
	id_genero = request.form["genero"]
	libro = Libro.query.filter_by(id_libro=int(id_libro)).first()
	libro.nombre_libro = nombre_libro
	libro.fecha_publicacion = fecha_publicacion
	libro.numero_paginas = numero_paginas
	libro.formato = formato
	libro.volumen = volumen
	libro.resumen = resumen
	libro.link = link
	libro.id_editorial = id_editorial
	libro.id_autor = id_autor
	libro.id_genero = id_genero
	db.session.commit()
	return redirect("/verlibro")
#Redireccion al Registrar Libro
@app.route("/libro")
def libro():
	consulta_editorial = Editorial.query.all()
	consulta_genero = Genero.query.all()
	consulta_autor = Autor.query.all()
	return render_template("registrarlibro.html", consulta_editorial=consulta_editorial, consulta_genero=consulta_genero, consulta_autor= consulta_autor)

#----------------------------------------  Registrar Autor 
@app.route("/registrar_autor", methods=["POST"])
def registrar_autor():
	nombre_autor = request.form["nombre_autor"]
	fecha_nacimiento = request.form["fecha_nacimiento"]
	nacionalidad = request.form["nacionalidad"]
	autor = Autor(nombre_autor=nombre_autor,fecha_nacimiento=fecha_nacimiento,nacionalidad=nacionalidad)
	db.session.add(autor)
	db.session.commit()
	return render_template("registrarautor.html")
#Ver Autor
@app.route("/verautor")
def verautor():
	consulta = Autor.query.all()
	return render_template("verautor.html", consulta = consulta)
#Eliminar Autor
@app.route("/eliminarautor/<id>")
def eliminarautor(id):
	Autor.query.filter_by(nombre_autor = id).delete()
	db.session.commit()
	return redirect("/verautor")
#Ir a modificar Autor
@app.route("/editarautor/<id>")
def editarautor(id):
	nota = Autor.query.filter_by(nombre_autor = id).first()
	return render_template("modificarautor.html", nota = nota)
#Modificar Autor
@app.route("/modificarautor", methods=['POST'])
def modificarNota():
	id_autor = request.form['id_autor']
	nombre_autor = request.form['nombre_autor']
	fecha_nacimiento = request.form['fecha_nacimiento']
	nacionalidad = request.form['nacionalidad']
	autor = Autor.query.filter_by(id_autor=int(id_autor)).first()
	autor.nombre_autor = nombre_autor
	autor.fecha_nacimiento = fecha_nacimiento
	autor.nacionalidad = nacionalidad
	db.session.commit()
	return redirect("/verautor")
#Redireccion al Registrar Autor
@app.route("/autor")
def autor():
	return render_template("registrarautor.html")

#----------------------------------------  Registrar Genero 
@app.route("/registrar_genero", methods=["POST"])
def registrar_genero():
	tipo_genero = request.form["tipo_genero"]
	genero = Genero(tipo_genero=tipo_genero)
	db.session.add(genero)
	db.session.commit()
	return render_template("registrargenero.html")
#Ver Genero
@app.route("/vergenero")
def veregenero():
	consulta = Genero.query.all()
	return render_template("vergenero.html", consulta = consulta)
#Eliminar Genero
@app.route("/eliminargenero/<id>")
def eliminargenero(id):
	Genero.query.filter_by(tipo_genero = id).delete()
	db.session.commit()
	return redirect("/vergenero")
#Ir a modificar Genero
@app.route("/editargenero/<id>")
def editargenero(id):
	nota = Genero.query.filter_by(tipo_genero = id).first()
	return render_template("modificargenero.html", nota = nota)
#Modificar Genero
@app.route("/modificargenero", methods=['POST'])
def modificargenero():
	id_genero = request.form['id_genero']
	tipo_genero = request.form['tipo_genero']
	genero = Genero.query.filter_by(id_genero=int(id_genero)).first()
	genero.tipo_genero = tipo_genero
	db.session.commit()
	return redirect("/vergenero")
#Redireccion al Registrar Genero
@app.route("/genero")
def genero():
	return render_template("registrargenero.html")

#----------------------------------------  Registrar Editorial 
@app.route("/registrar_editorial", methods=["POST"])
def registrar_editorial():
	nombre_editorial = request.form["nombre_editorial"]
	editorial = Editorial(nombre_editorial=nombre_editorial)
	db.session.add(editorial)
	db.session.commit()
	return render_template("registrareditorial.html")
#Ver Editorial
@app.route("/vereditorial")
def vereditorial():
	consulta = Editorial.query.all()
	return render_template("vereditorial.html", consulta = consulta)
#Eliminar Editorial
@app.route("/eliminareditorial/<id>")
def eliminareditorial(id):
	Editorial.query.filter_by(nombre_editorial = id).delete()
	db.session.commit()
	return redirect("/vereditorial")
#Ir a modificar Editorial
@app.route("/editareditorial/<id>")
def editareditorial(id):
	nota = Editorial.query.filter_by(nombre_editorial = id).first()
	return render_template("modificareditorial.html", nota = nota)
#Modificar Editorial
@app.route("/modificareditorial", methods=['POST'])
def modificareditorial():
	id_editorial = request.form['id_editorial']
	nombre_editorial = request.form['nombre_editorial']
	editorial = Editorial.query.filter_by(id_editorial=int(id_editorial)).first()
	editorial.nombre_editorial = nombre_editorial
	db.session.commit()
	return redirect("/vereditorial")
#Redireccion al Registrar Editorial
@app.route("/editorial")
def editorial():
	return render_template("registrareditorial.html")

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)#El debug=True para que se actualize conforme modifico codigo  