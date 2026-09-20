BEGIN;

-- IMPORTANTE: hacer respaldo antes de ejecutar esta migración sobre una BD existente.
-- La eliminación de insignias es intencional porque MAREVA utilizará NIVELES como sistema de gamificación.

DROP TABLE IF EXISTS promocion_insignia CASCADE;
DROP TABLE IF EXISTS cliente_insignia CASCADE;
DROP TABLE IF EXISTS insignia CASCADE;

ALTER TABLE cliente DROP COLUMN IF EXISTS direccion;
ALTER TABLE proveedor DROP COLUMN IF EXISTS direccion;
ALTER TABLE alojamiento DROP COLUMN IF EXISTS direccion;

ALTER TABLE cliente
    ADD COLUMN IF NOT EXISTS acepta_politica_no_reembolso BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS fecha_aceptacion_politica TIMESTAMP,
    ADD COLUMN IF NOT EXISTS version_politica VARCHAR(20) NOT NULL DEFAULT '1.0';


-- Mejoras MAREVA: contingencias/reembolsos y preferencias lingüísticas
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS motivo_cancelacion TEXT;
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS reembolso_estado VARCHAR(30);
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS reembolso_fecha TIMESTAMP;
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS precio_total NUMERIC(12,2);
ALTER TABLE viajero_reserva ADD COLUMN IF NOT EXISTS idioma VARCHAR(50) NOT NULL DEFAULT 'Español';

-- Videos promocionales (destino, paquete e inicio)
ALTER TABLE destino ADD COLUMN IF NOT EXISTS video_url VARCHAR(255);
ALTER TABLE paquete_turistico ADD COLUMN IF NOT EXISTS video_url VARCHAR(255);

COMMIT;

-- Promociones demo visibles durante septiembre de 2026.
UPDATE promocion SET fecha_inicio='2026-08-15', fecha_fin='2026-09-30', descripcion='10% de descuento para escapadas de temporada' WHERE codigo='VERANO10';
UPDATE promocion SET fecha_inicio='2026-09-01', fecha_fin='2026-10-31' WHERE codigo='PAREJA20';
UPDATE promocion SET fecha_inicio='2026-09-01', fecha_fin='2026-11-30' WHERE codigo='MOCHILA15';
