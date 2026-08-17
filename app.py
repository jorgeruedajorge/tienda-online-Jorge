from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from config import Config

from models import (
    db,
    Producto,
    ProductoFisico,
    ProductoDigital,
    ProductoPerecible,
    Usuario,
    Carrito,
    Pedido,
    DetallePedido
)

from auth import login_requerido, rol_requerido

# ==========================================
# CONFIGURACIÓN DE FLASK
# ==========================================

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)


# ==========================================
# FUNCIÓN: COMPROBAR ADMINISTRADOR
# ==========================================

def usuario_es_admin():

    return session.get("usuario_rol") == "admin"


# ==========================================
# PÁGINA PRINCIPAL - CATÁLOGO
# ==========================================

@app.route("/")
def inicio():

    productos = Producto.query.filter_by(
        activo=True
    ).all()

    return render_template(
        "index.html",
        productos=productos
    )


# ==========================================
# DETALLE DE PRODUCTO
# ==========================================

@app.route("/producto/<int:producto_id>")
def detalle_producto(producto_id):

    producto = Producto.query.get_or_404(
        producto_id
    )

    return render_template(
        "detalle.html",
        producto=producto
    )


# ==========================================
# EDITAR PRODUCTO
# SOLO ADMIN
# ==========================================

@app.route(
    "/productos/<int:producto_id>/editar",
    methods=["GET", "POST"]
)
def editar_producto(producto_id):

    # --------------------------------------
    # PROTECCIÓN ADMIN
    # --------------------------------------

    @app.route(
        "/productos/<int:producto_id>/editar",
        methods=["GET", "POST"]
    )
    @rol_requerido("admin")
    def editar_producto(producto_id):

        flash(
            "Solo los administradores pueden editar productos.",
            "danger"
        )

        return redirect(
            url_for("inicio")
        )


    # --------------------------------------
    # BUSCAR PRODUCTO
    # --------------------------------------

    producto = Producto.query.get_or_404(
        producto_id
    )


    # --------------------------------------
    # ACTUALIZAR PRODUCTO
    # --------------------------------------

    if request.method == "POST":

        try:

            producto.nombre = request.form[
                "nombre"
            ].strip()

            producto.precio_base = float(
                request.form[
                    "precio_base"
                ]
            )

            producto.stock = int(
                request.form[
                    "stock"
                ]
            )

            db.session.commit()

            flash(
                "Producto actualizado correctamente.",
                "success"
            )

            return redirect(
                url_for(
                    "detalle_producto",
                    producto_id=producto.id
                )
            )

        except ValueError:

            return (
                "Revisa que el precio y el stock sean válidos.",
                400
            )


    # --------------------------------------
    # MOSTRAR FORMULARIO
    # --------------------------------------

    return render_template(
        "editar.html",
        producto=producto
    )


# ==========================================
# DESACTIVAR PRODUCTO
# SOLO ADMIN
# ==========================================

@app.route(
    "/productos/<int:producto_id>/desactivar",
    methods=["POST"]
)
def desactivar_producto(producto_id):

    # --------------------------------------
    # PROTECCIÓN ADMIN
    # --------------------------------------

    @app.route(
        "/productos/<int:producto_id>/desactivar",
        methods=["POST"]
    )
    @rol_requerido("admin")
    def desactivar_producto(producto_id):

        flash(
            "Solo los administradores pueden desactivar productos.",
            "danger"
        )

        return redirect(
            url_for("inicio")
        )


    # --------------------------------------
    # BUSCAR PRODUCTO
    # --------------------------------------

    producto = Producto.query.get_or_404(
        producto_id
    )


    # --------------------------------------
    # DESACTIVAR
    # --------------------------------------

    producto.activo = False

    db.session.commit()

    flash(
        "Producto desactivado correctamente.",
        "success"
    )

    return redirect(
        url_for("inicio")
    )


# ==========================================
# CREAR NUEVO PRODUCTO
# SOLO ADMIN
# ==========================================

@app.route(
    "/producto/nuevo",
    methods=["GET", "POST"]
)
def nuevo_producto():

    # --------------------------------------
    # PROTECCIÓN ADMIN
    # --------------------------------------

    @app.route(
        "/producto/nuevo",
        methods=["GET", "POST"]
    )
    @rol_requerido("admin")
    def nuevo_producto():

        flash(
            "Solo los administradores pueden agregar productos.",
            "danger"
        )

        return redirect(
            url_for("inicio")
        )


    # --------------------------------------
    # MOSTRAR FORMULARIO
    # --------------------------------------

    if request.method == "GET":

        return render_template(
            "nuevo_producto.html"
        )


    # --------------------------------------
    # RECIBIR DATOS
    # --------------------------------------

    tipo = request.form.get("tipo")

    codigo = request.form.get(
        "codigo"
    )

    nombre = request.form.get(
        "nombre"
    )


    # --------------------------------------
    # PRECIO Y STOCK
    # --------------------------------------

    try:

        precio_base = float(
            request.form.get(
                "precio_base"
            )
        )

        stock = int(
            request.form.get(
                "stock"
            )
        )

    except (TypeError, ValueError):

        flash(
            "El precio y el stock deben ser números válidos.",
            "danger"
        )

        return redirect(
            url_for("nuevo_producto")
        )


    # ======================================
    # PRODUCTO FÍSICO
    # ======================================

    if tipo == "fisico":

        try:

            peso_kg = float(
                request.form.get(
                    "peso_kg"
                )
            )

            costo_envio_por_kg = float(
                request.form.get(
                    "costo_envio_por_kg"
                )
            )

        except (TypeError, ValueError):

            flash(
                "El peso y el costo de envío deben ser números válidos.",
                "danger"
            )

            return redirect(
                url_for("nuevo_producto")
            )


        producto = ProductoFisico(

            codigo=codigo,

            nombre=nombre,

            precio_base=precio_base,

            stock=stock,

            peso_kg=peso_kg,

            costo_envio_por_kg=costo_envio_por_kg

        )


    # ======================================
    # PRODUCTO DIGITAL
    # ======================================

    elif tipo == "digital":

        licencia = request.form.get(
            "licencia"
        )


        producto = ProductoDigital(

            codigo=codigo,

            nombre=nombre,

            precio_base=precio_base,

            stock=stock,

            licencia=licencia

        )


    # ======================================
    # PRODUCTO PERECIBLE
    # ======================================

    elif tipo == "perecible":

        try:

            dias_para_vencer = int(
                request.form.get(
                    "dias_para_vencer"
                )
            )

        except (TypeError, ValueError):

            flash(
                "Los días para vencer deben ser un número.",
                "danger"
            )

            return redirect(
                url_for("nuevo_producto")
            )


        producto = ProductoPerecible(

            codigo=codigo,

            nombre=nombre,

            precio_base=precio_base,

            stock=stock,

            dias_para_vencer=dias_para_vencer

        )


    # ======================================
    # TIPO NO VÁLIDO
    # ======================================

    else:

        flash(
            "Tipo de producto no válido.",
            "danger"
        )

        return redirect(
            url_for("nuevo_producto")
        )


    # ======================================
    # GUARDAR EN POSTGRESQL
    # ======================================

    try:

        db.session.add(
            producto
        )

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "No se pudo guardar el producto. "
            "Verifica que el código no esté repetido.",
            "danger"
        )

        return redirect(
            url_for("nuevo_producto")
        )


    # --------------------------------------
    # CONFIRMACIÓN
    # --------------------------------------

    flash(
        "Producto creado correctamente.",
        "success"
    )

    return redirect(
        url_for("inicio")
    )

# ==========================================
# AGREGAR PRODUCTO AL CARRITO
# SOLO USUARIOS LOGUEADOS
# ==========================================

@app.route(
    "/carrito/agregar/<int:producto_id>",
    methods=["POST"]
)
@login_requerido
def agregar_al_carrito(producto_id):

    # --------------------------------------
    # COMPROBAR QUE HAYA SESIÓN
    # --------------------------------------

    if "usuario_id" not in session:

        flash(
            "Debes iniciar sesión para agregar productos al carrito.",
            "warning"
        )

        return redirect(
            url_for("login")
        )


    # --------------------------------------
    # BUSCAR PRODUCTO
    # --------------------------------------

    producto = Producto.query.get_or_404(
        producto_id
    )


    # --------------------------------------
    # COMPROBAR QUE ESTÉ ACTIVO
    # --------------------------------------

    if not producto.activo:

        flash(
            "Este producto no está disponible.",
            "danger"
        )

        return redirect(
            url_for(
                "inicio"
            )
        )


    # --------------------------------------
    # COMPROBAR STOCK
    # --------------------------------------

    if producto.stock <= 0:

        flash(
            "Este producto no tiene stock disponible.",
            "danger"
        )

        return redirect(
            url_for(
                "detalle_producto",
                producto_id=producto.id
            )
        )


    # --------------------------------------
    # BUSCAR SI YA ESTÁ EN EL CARRITO
    # --------------------------------------

    item = Carrito.query.filter_by(

        usuario_id=session["usuario_id"],

        producto_id=producto.id

    ).first()


    # --------------------------------------
    # SI YA EXISTE
    # --------------------------------------

    if item:

        if item.cantidad >= producto.stock:

            flash(
                "No puedes agregar más unidades de este producto.",
                "warning"
            )

            return redirect(
                url_for(
                    "detalle_producto",
                    producto_id=producto.id
                )
            )


        item.cantidad += 1


    # --------------------------------------
    # SI NO EXISTE
    # --------------------------------------

    else:

        item = Carrito(

            usuario_id=session["usuario_id"],

            producto_id=producto.id,

            cantidad=1

        )

        db.session.add(
            item
        )


    # --------------------------------------
    # GUARDAR
    # --------------------------------------

    db.session.commit()


    flash(
        f"{producto.nombre} fue agregado al carrito.",
        "success"
    )


    return redirect(
        url_for(
            "detalle_producto",
            producto_id=producto.id
        )
    )

# ==========================================
# VER CARRITO
# ==========================================

@app.route("/carrito")
@login_requerido
def ver_carrito():

    # Comprobar que haya sesión

    if "usuario_id" not in session:

        flash(
            "Debes iniciar sesión para ver tu carrito.",
            "warning"
        )

        return redirect(
            url_for("login")
        )


    # Obtener productos del carrito
    items = Carrito.query.filter_by(
        usuario_id=session["usuario_id"]
    ).all()


    # Calcular total

    total = sum(
        item.subtotal()
        for item in items
    )


    return render_template(
        "carrito.html",
        items=items,
        total=total
    )

# ==========================================
# AUMENTAR CANTIDAD
# ==========================================

@app.route(
    "/carrito/aumentar/<int:item_id>",
    methods=["POST"]
)
@login_requerido
def aumentar_cantidad(item_id):

    if "usuario_id" not in session:
        flash(
            "Debes iniciar sesión.",
            "warning"
        )
        return redirect(url_for("login"))

    item = Carrito.query.get_or_404(item_id)

    # Verificar que el carrito pertenece al usuario
    if item.usuario_id != session["usuario_id"]:
        flash(
            "No tienes permiso para modificar este carrito.",
            "danger"
        )
        return redirect(url_for("ver_carrito"))

    # Comprobar stock
    if item.cantidad >= item.producto.stock:

        flash(
            "No hay más unidades disponibles.",
            "warning"
        )

        return redirect(url_for("ver_carrito"))

    item.cantidad += 1

    db.session.commit()

    return redirect(
        url_for("ver_carrito")
    )


# ==========================================
# DISMINUIR CANTIDAD
# ==========================================

@app.route(
    "/carrito/disminuir/<int:item_id>",
    methods=["POST"]
)
@login_requerido
def disminuir_cantidad(item_id):

    if "usuario_id" not in session:
        flash(
            "Debes iniciar sesión.",
            "warning"
        )
        return redirect(url_for("login"))

    item = Carrito.query.get_or_404(item_id)

    if item.usuario_id != session["usuario_id"]:
        flash(
            "No tienes permiso para modificar este carrito.",
            "danger"
        )
        return redirect(url_for("ver_carrito"))

    if item.cantidad > 1:

        item.cantidad -= 1

        db.session.commit()

    else:

        db.session.delete(item)

        db.session.commit()

    return redirect(
        url_for("ver_carrito")
    )


# ==========================================
# ELIMINAR DEL CARRITO
# ==========================================

@app.route(
    "/carrito/eliminar/<int:item_id>",
    methods=["POST"]
)
@login_requerido
def eliminar_del_carrito(item_id):

    if "usuario_id" not in session:
        flash(
            "Debes iniciar sesión.",
            "warning"
        )
        return redirect(url_for("login"))

    item = Carrito.query.get_or_404(item_id)

    if item.usuario_id != session["usuario_id"]:

        flash(
            "No tienes permiso para eliminar este producto.",
            "danger"
        )

        return redirect(
            url_for("ver_carrito")
        )

    db.session.delete(item)

    db.session.commit()

    flash(
        "Producto eliminado del carrito.",
        "success"
    )

    return redirect(
        url_for("ver_carrito")
    )


# ==========================================
# FINALIZAR COMPRA
# SOLO USUARIOS LOGUEADOS
# ==========================================

@app.route("/checkout", methods=["POST"])
@login_requerido
def checkout():

    # --------------------------------------
    # COMPROBAR SESIÓN
    # --------------------------------------

    if "usuario_id" not in session:

        flash(
            "Debes iniciar sesión para realizar una compra.",
            "warning"
        )

        return redirect(
            url_for("login")
        )


    # --------------------------------------
    # OBTENER CARRITO DEL USUARIO
    # --------------------------------------

    items = Carrito.query.filter_by(
        usuario_id=session["usuario_id"]
    ).all()


    if not items:

        flash(
            "Tu carrito está vacío.",
            "warning"
        )

        return redirect(
            url_for("ver_carrito")
        )


    # --------------------------------------
    # VERIFICAR STOCK ANTES DE COMPRAR
    # --------------------------------------

    for item in items:

        producto = item.producto

        if not producto.activo:

            flash(
                f"El producto '{producto.nombre}' ya no está disponible.",
                "danger"
            )

            return redirect(
                url_for("ver_carrito")
            )


        if item.cantidad > producto.stock:

            flash(
                f"No hay suficiente stock de '{producto.nombre}'. "
                f"Stock disponible: {producto.stock}.",
                "danger"
            )

            return redirect(
                url_for("ver_carrito")
            )


    # --------------------------------------
    # CREAR PEDIDO
    # --------------------------------------

    pedido = Pedido(
        usuario_id=session["usuario_id"],
        total=0,
        estado="confirmado"
    )

    db.session.add(pedido)

    # Necesitamos que el pedido tenga ID antes
    # de crear sus detalles.
    db.session.flush()


    total = 0


    # --------------------------------------
    # CREAR DETALLES Y DESCONTAR STOCK
    # --------------------------------------

    for item in items:

        producto = item.producto

        # Guardar el precio actual en el momento
        # de realizar la compra.
        precio = producto.precio_final()

        subtotal = precio * item.cantidad

        detalle = DetallePedido(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=item.cantidad,
            precio=precio,
            subtotal=subtotal
        )

        db.session.add(detalle)

        # Descontar stock
        producto.stock -= item.cantidad

        total += subtotal


    # --------------------------------------
    # ACTUALIZAR TOTAL DEL PEDIDO
    # --------------------------------------

    pedido.total = total


    # --------------------------------------
    # VACIAR CARRITO
    # --------------------------------------

    for item in items:

        db.session.delete(item)


    # --------------------------------------
    # GUARDAR TODO
    # --------------------------------------

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "No se pudo completar la compra. "
            "No se realizaron cambios.",
            "danger"
        )

        return redirect(
            url_for("ver_carrito")
        )


    # --------------------------------------
    # CONFIRMACIÓN
    # --------------------------------------

    flash(
        f"Compra realizada correctamente. "
        f"Pedido #{pedido.id}. "
        f"Total: ${pedido.total:.2f}",
        "success"
    )


    return redirect(
        url_for(
            "pedido_confirmado",
            pedido_id=pedido.id
        )
    )


# ==========================================
# PEDIDO CONFIRMADO
# SOLO USUARIOS LOGUEADOS
# ==========================================

@app.route(
    "/pedido/<int:pedido_id>/confirmado"
)
def pedido_confirmado(pedido_id):

    if "usuario_id" not in session:

        flash(
            "Debes iniciar sesión.",
            "warning"
        )

        return redirect(
            url_for("login")
        )


    pedido = Pedido.query.get_or_404(
        pedido_id
    )


    # El usuario solamente puede ver
    # sus propios pedidos.

    if pedido.usuario_id != session["usuario_id"]:

        flash(
            "No tienes permiso para ver este pedido.",
            "danger"
        )

        return redirect(
            url_for("inicio")
        )


    return render_template(
        "pedido_confirmado.html",
        pedido=pedido
    )


# ==========================================
# REGISTRO DE USUARIO
# ==========================================

@app.route(
    "/registro",
    methods=["GET", "POST"]
)
def registro():

    if request.method == "POST":

        nombre = request.form[
            "nombre"
        ].strip()

        email = request.form[
            "email"
        ].strip().lower()

        password = request.form[
            "password"
        ]


        # ----------------------------------
        # VALIDAR DATOS
        # ----------------------------------

        if not nombre or not email or not password:

            flash(
                "Todos los campos son obligatorios.",
                "danger"
            )

            return render_template(
                "registro.html"
            )


        if len(password) < 6:

            flash(
                "La contraseña debe tener al menos 6 caracteres.",
                "danger"
            )

            return render_template(
                "registro.html"
            )


        # ----------------------------------
        # COMPROBAR EMAIL
        # ----------------------------------

        usuario_existente = Usuario.query.filter_by(
            email=email
        ).first()


        if usuario_existente:

            flash(
                "Ya existe una cuenta con ese correo.",
                "danger"
            )

            return render_template(
                "registro.html"
            )


        # ----------------------------------
        # CREAR USUARIO
        # ----------------------------------

        usuario = Usuario(

            nombre=nombre,

            email=email,

            rol="cliente"

        )


        # ----------------------------------
        # GUARDAR CONTRASEÑA COMO HASH
        # ----------------------------------

        usuario.set_password(
            password
        )


        db.session.add(
            usuario
        )

        db.session.commit()


        flash(
            "Cuenta creada correctamente. Ya puedes iniciar sesión.",
            "success"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "registro.html"
    )


# ==========================================
# LOGIN
# ==========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip().lower()

        password = request.form[
            "password"
        ]


        # ----------------------------------
        # BUSCAR USUARIO
        # ----------------------------------

        usuario = Usuario.query.filter_by(
            email=email
        ).first()


        # ----------------------------------
        # VERIFICAR CONTRASEÑA
        # ----------------------------------

        if usuario and usuario.check_password(
            password
        ):

            # Guardar datos en sesión

            session["usuario_id"] = usuario.id

            session["usuario_nombre"] = usuario.nombre

            session["usuario_rol"] = usuario.rol


            flash(
                f"Bienvenido, {usuario.nombre}.",
                "success"
            )


            return redirect(
                url_for("inicio")
            )


        # ----------------------------------
        # LOGIN INCORRECTO
        # ----------------------------------

        flash(
            "Correo o contraseña incorrectos.",
            "danger"
        )


    return render_template(
        "login.html"
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(
        url_for("inicio")
    )


# ==========================================
# EJECUTAR APLICACIÓN
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )