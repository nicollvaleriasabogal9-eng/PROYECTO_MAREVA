class Cliente:
    def __init__(self, id , nombre, apellido, tipo_documento, numero_documento, telefono, correo, password, rol, codigo_referido, fecha_registro, estado, intentos_fallidos, bloqueado_hasta, id_nivel):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.tipo_documento = tipo_documento
        self.numero_documento = numero_documento
        self.telefono = telefono
        self.correo = correo
        self.password = password
        self.rol = rol
        self.codigo_referido = codigo_referido
        self.fecha_registro = fecha_registro
        self.estado = estado
        self.intentos_fallidos = intentos_fallidos
        self.bloqueado_hasta = bloqueado_hasta
        self.id_nivel = id_nivel