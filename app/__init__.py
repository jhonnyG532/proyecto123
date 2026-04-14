from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    from flask import Flask
    from flask_jwt_extended import JWTManager
    import config
    from app.models import db, Producto, Configuracion, Usuario, Categoria, Mesa

    app = Flask(__name__)
    app.config.from_object(config.Config)
    db.init_app(app)
    jwt = JWTManager(app)

    from app.routes import main_bp
    from app.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

        if not Configuracion.query.first():
            db.session.add(Configuracion(
                nombre_negocio='Ovni Burger',
                direccion='Barbosa, Santander',
                telefono='+57 321 395 2402',
                nit='901.234.567-8',
                mensaje_pie='¡Pide desde WhatsApp!',
                instagram='burger.ovni',
            ))

        if not Categoria.query.first():
            for c in [('hamburguesas', 'bi-ufo', 1), ('hotdogs', 'bi-hot', 2), ('crateres', 'bi-french-fries', 3)]:
                db.session.add(Categoria(nombre=c[0], icono=c[1], orden=c[2]))

        if not Producto.query.first():
            productos = [
                ('HAM01', 'La Órbita Clásica', 'Carne 100% premium, cebolla grille, jamón, queso cheddar, vegetales frescos, salsa secreta.', 18000, 'hamburguesas', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400'),
                ('HAM01P', 'La Órbita Clásica + Papa', 'La clásica + papa frita crujiente.', 20000, 'hamburguesas', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400'),
                ('HAM02', 'Pollo Estelar', 'Salsa de champiñones, pollo, carne, tocineta y salsa de la casa.', 23000, 'hamburguesas', 'https://images.unsplash.com/photo-1512151373240-7eb199247f61?w=400'),
                ('HAM02P', 'Pollo Estelar + Papa', 'Pollo Estelar + papa frita.', 25000, 'hamburguesas', 'https://images.unsplash.com/photo-1512151373240-7eb199247f61?w=400'),
                ('HAM03', 'Cápsula BBQ', 'Costillas BBQ, carne, jamón, queso, vegetales y salsa ahumada.', 25000, 'hamburguesas', 'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400'),
                ('HAM03P', 'Cápsula BBQ + Papa', 'Cápsula BBQ + papa frita.', 27000, 'hamburguesas', 'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400'),
                ('HOT01', 'Nebulosa Clásica', 'Salchicha premium, queso, papa ripio, pico de gallo y salsas.', 15000, 'hotdogs', 'https://images.unsplash.com/photo-1612392062628-94e981d6112e?w=400'),
                ('HOT01P', 'Nebulosa + Papa', 'Nebulosa + papa frita.', 17000, 'hotdogs', 'https://images.unsplash.com/photo-1612392062628-94e981d6112e?w=400'),
                ('HOT02', 'Nebulosa Especial', 'Salchicha con todo: pollo, tocineta, queso, papa ripio.', 18000, 'hotdogs', 'https://images.unsplash.com/photo-1612392062628-94e981d6112e?w=400'),
                ('CRAT01', 'Súper Nova', 'Papa con todo: salchicha, pollo, queso, plátano y huevos.', 25000, 'crateres', 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400'),
                ('CRAT02', 'Mini Nova', 'Papa, salchicha, pollo y queso.', 13000, 'crateres', 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400'),
            ]
            for p in productos:
                db.session.add(Producto(codigo=p[0], nombre=p[1], descripcion=p[2], precio=p[3], categoria=p[4], imagen=p[5]))

        if not Usuario.query.filter_by(username='jhonny').first():
            admin = Usuario(username='jhonny')
            admin.set_password('5331')
            db.session.add(admin)

        db.session.commit()

    return app