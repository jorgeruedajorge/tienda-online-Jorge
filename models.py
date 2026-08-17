from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


db = SQLAlchemy()


# ==========================================
# USUARIO
# ==========================================

class Usuario(db.Model):

    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    rol = db.Column(
        db.String(20),
        nullable=False,
        default="cliente"
    )

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    # ======================================
    # RELACIONES
    # ======================================

    carrito_items = db.relationship(
        "Carrito",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    pedidos = db.relationship(
        "Pedido",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )


    # ======================================
    # CONTRASEÑA
    # ======================================

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )


    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


    def es_admin(self):

        return self.rol == "admin"


    def __repr__(self):

        return f"<Usuario {self.email} ({self.rol})>"


# ==========================================
# PRODUCTO
# ==========================================

class Producto(db.Model):

    __tablename__ = "productos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    codigo = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    precio_base = db.Column(
        db.Float,
        nullable=False
    )

    stock = db.Column(
        db.Integer,
        default=0
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    peso_kg = db.Column(
        db.Float,
        nullable=True
    )

    costo_envio_por_kg = db.Column(
        db.Float,
        nullable=True
    )

    licencia = db.Column(
        db.String(20),
        nullable=True
    )

    dias_para_vencer = db.Column(
        db.Integer,
        nullable=True
    )

    tipo = db.Column(
        db.String(30)
    )


    # ======================================
    # HERENCIA
    # ======================================

    __mapper_args__ = {
        "polymorphic_identity": "producto",
        "polymorphic_on": tipo
    }


    # ======================================
    # RELACIONES
    # ======================================

    carrito_items = db.relationship(
        "Carrito",
        back_populates="producto"
    )

    detalles_pedido = db.relationship(
        "DetallePedido",
        back_populates="producto"
    )


    # ======================================
    # PRECIO FINAL
    # ======================================

    def precio_final(self):

        return self.precio_base


    # ======================================
    # FICHA
    # ======================================

    def ficha(self):

        return (
            f"[{self.codigo}] {self.nombre} "
            f"| Precio final: ${self.precio_final():.2f} "
            f"| Stock: {self.stock}"
        )


    def __repr__(self):

        return (
            f"<{self.__class__.__name__} "
            f"{self.codigo} - {self.nombre}>"
        )


# ==========================================
# PRODUCTO FÍSICO
# ==========================================

class ProductoFisico(Producto):

    __mapper_args__ = {
        "polymorphic_identity": "fisico"
    }


    def precio_final(self):

        envio = (
            (self.peso_kg or 0)
            *
            (self.costo_envio_por_kg or 0)
        )

        return self.precio_base + envio


# ==========================================
# PRODUCTO DIGITAL
# ==========================================

class ProductoDigital(Producto):

    __mapper_args__ = {
        "polymorphic_identity": "digital"
    }


    MULTIPLICADORES = {
        "personal": 1.0,
        "comercial": 2.5,
        "educativa": 0.6,
    }


    def precio_final(self):

        multiplicador = self.MULTIPLICADORES.get(
            self.licencia,
            1.0
        )

        return self.precio_base * multiplicador


# ==========================================
# PRODUCTO PERECIBLE
# ==========================================

class ProductoPerecible(Producto):

    __mapper_args__ = {
        "polymorphic_identity": "perecible"
    }


    def precio_final(self):

        dias = self.dias_para_vencer


        if dias is None:

            return self.precio_base


        if dias <= 3:

            return self.precio_base * 0.50


        elif dias <= 7:

            return self.precio_base * 0.80


        return self.precio_base


# ==========================================
# CARRITO
# ==========================================

class Carrito(db.Model):

    __tablename__ = "carrito"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id"
        ),
        nullable=False
    )


    producto_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "productos.id"
        ),
        nullable=False
    )


    cantidad = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )


    fecha_agregado = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    # ======================================
    # RELACIONES
    # ======================================

    usuario = db.relationship(
        "Usuario",
        back_populates="carrito_items"
    )


    producto = db.relationship(
        "Producto",
        back_populates="carrito_items"
    )


    # ======================================
    # SUBTOTAL
    # ======================================

    def subtotal(self):

        return (
            self.producto.precio_final()
            *
            self.cantidad
        )


    def __repr__(self):

        return (
            f"<Carrito "
            f"usuario={self.usuario_id} "
            f"producto={self.producto_id} "
            f"cantidad={self.cantidad}>"
        )


# ==========================================
# PEDIDO
# ==========================================

class Pedido(db.Model):

    __tablename__ = "pedidos"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id"
        ),
        nullable=False
    )


    total = db.Column(
        db.Float,
        nullable=False,
        default=0
    )


    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    estado = db.Column(
        db.String(30),
        nullable=False,
        default="pendiente"
    )


    # ======================================
    # RELACIONES
    # ======================================

    usuario = db.relationship(
        "Usuario",
        back_populates="pedidos"
    )


    detalles = db.relationship(
        "DetallePedido",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )


    def __repr__(self):

        return (
            f"<Pedido "
            f"id={self.id} "
            f"usuario={self.usuario_id} "
            f"total={self.total}>"
        )


# ==========================================
# DETALLE DEL PEDIDO
# ==========================================

class DetallePedido(db.Model):

    __tablename__ = "detalle_pedido"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "pedidos.id"
        ),
        nullable=False
    )


    producto_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "productos.id"
        ),
        nullable=False
    )


    cantidad = db.Column(
        db.Integer,
        nullable=False
    )


    precio = db.Column(
        db.Float,
        nullable=False
    )


    subtotal = db.Column(
        db.Float,
        nullable=False
    )


    # ======================================
    # RELACIONES
    # ======================================

    pedido = db.relationship(
        "Pedido",
        back_populates="detalles"
    )


    producto = db.relationship(
        "Producto",
        back_populates="detalles_pedido"
    )


    def __repr__(self):

        return (
            f"<DetallePedido "
            f"pedido={self.pedido_id} "
            f"producto={self.producto_id} "
            f"cantidad={self.cantidad}>"
        )