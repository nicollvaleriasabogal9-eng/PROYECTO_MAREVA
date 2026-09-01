from flask import jsonify, redirect, render_template, request, session, url_for

from services.paquete_services import PaqueteService


class FavoritosController:

    def __init__(self):
        self.service = PaqueteService()

    @staticmethod
    def _ids_favoritos():
        return [
            int(id_paquete)
            for id_paquete in session.get("favoritos", [])
            if str(id_paquete).isdigit()
        ]

    def listar(self):
        ids = self._ids_favoritos()
        paquetes = self.service.listar_por_ids(ids)
        return render_template("cliente/favoritos.html", paquetes=paquetes)

    def alternar(self, id_paquete):
        paquete = self.service.obtener_para_editar(id_paquete)
        if not paquete or paquete.get("estado") != "activo":
            return jsonify({"ok": False, "error": "Paquete no disponible."}), 404

        favoritos = self._ids_favoritos()
        if id_paquete in favoritos:
            favoritos.remove(id_paquete)
            agregado = False
        else:
            favoritos.append(id_paquete)
            agregado = True

        # Se conserva únicamente en la sesión; nunca se escribe en PostgreSQL.
        session["favoritos"] = favoritos
        session.modified = True
        respuesta = {
            "ok": True,
            "agregado": agregado,
            "total": len(favoritos),
        }
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(respuesta)
        return redirect(request.referrer or url_for("favoritos.listar"))
