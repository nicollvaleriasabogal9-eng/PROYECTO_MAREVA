from abc import ABC, abstractmethod


class PaqueteBase(ABC):
    def __init__(self, data: dict):
        self._data = data

    def get_id(self):
        return self._data["id_paquete"]

    def get_slug(self):
        return self._data["slug"]

    def get_nombre(self):
        return self._data["nombre"]

    def get_precio(self):
        return float(self._data["precio"])

    def get_categoria(self):
        return self._data["categoria"]

    def to_dict(self):
        d = dict(self._data)
        d["precio_final"] = self.calcular_precio_final()
        return d

    @abstractmethod
    def calcular_precio_final(self):
        pass


class Playa(PaqueteBase):
    def calcular_precio_final(self):
        return round(self.get_precio() * 1.10, 2)


class Aventura(PaqueteBase):
    def calcular_precio_final(self):
        return round(self.get_precio() * 1.15, 2)


class Ecoturismo(PaqueteBase):
    def calcular_precio_final(self):
        return round(self.get_precio() * 1.08, 2)


class Cultural(PaqueteBase):
    def calcular_precio_final(self):
        return round(self.get_precio() * 0.95, 2)


class Ciudad(PaqueteBase):
    def calcular_precio_final(self):
        return round(self.get_precio() * 1.0, 2)


_FACTORY = {
    "playa": Playa,
    "aventura": Aventura,
    "ecoturismo": Ecoturismo,
    "cultural": Cultural,
    "ciudad": Ciudad,
    "montaña": Ecoturismo,
}


def factory_paquete(data: dict) -> PaqueteBase:
    categoria = (data.get("categoria") or "").lower()
    clase = _FACTORY.get(categoria, Cultural)
    return clase(data)