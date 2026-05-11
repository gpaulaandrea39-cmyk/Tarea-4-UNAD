"""
models/cliente.py
Clase Cliente con encapsulación, validaciones y excepciones personalizadas.
"""
import logging
import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
from datetime import datetime

# =================================================================
# 1. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS
# =================================================================
class SoftwareFJError(Exception):
    """Raíz de todos los errores del sistema Software FJ."""
    pass

class ClienteError(SoftwareFJError):
    """Raíz de errores relacionados con Cliente."""
    pass

class NombreInvalidoError(ClienteError): pass
class EmailInvalidoError(ClienteError): pass
class TelefonoInvalidoError(ClienteError): pass
class IDClienteInvalidoError(ClienteError): pass

# =================================================================
# 2. CONFIGURACIÓN DE LOGS (Manejo de archivos para errores)
# =================================================================
logging.basicConfig(
    filename='registro_eventos.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# =================================================================
# 3. ARQUITECTURA ORIENTADA A OBJETOS (Capa de Negocio)
# =================================================================

class EntidadGeneral(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad
        self._timestamp = datetime.now()

    @abstractmethod
    def validar_datos(self):
        """Obliga a las clases derivadas a implementar validaciones."""
        pass

class Cliente(EntidadGeneral):
    """Clase Cliente con encapsulación y validaciones estrictas."""
    def __init__(self, id_cliente, nombre, email, telefono):
        super().__init__(id_cliente)
        self.__id = id_cliente
        self.__nombre = nombre
        self.__email = email
        self.__telefono = telefono
        self.validar_datos() # Validación al instanciar

    def validar_datos(self):
        if not self.__id.isdigit():
            raise IDClienteInvalidoError("El ID debe contener solo números.")
        if len(self.__nombre) < 3:
            raise NombreInvalidoError("El nombre es demasiado corto (mín. 3 caracteres).")
        if "@" not in self.__email:
            raise EmailInvalidoError("El correo electrónico no tiene un formato válido.")
        if len(self.__telefono) < 7:
            raise TelefonoInvalidoError("El teléfono debe tener al menos 7 dígitos.")

    # Getters para la interfaz
    def obtener_info(self):
        return (self.__id, self.__nombre, self.__email, self.__telefono)

class GestorClientes:
    """Manejo de listas internas y lógica de almacenamiento."""
    def __init__(self):
        self.__clientes = []

    def agregar_cliente(self, id_c, nom, em, tel):
        try:
            # Crear objeto cliente (Dispara validaciones internas)
            nuevo = Cliente(id_c, nom, em, tel)
            self.__clientes.append(nuevo)
            logging.info(f"ÉXITO: Cliente {nom} registrado.")
            return nuevo
        except ClienteError as e:
            logging.warning(f"VALIDACIÓN: Fallo al registrar ID {id_c}: {e}")
            raise # Re-lanzar para la GUI
        except Exception as e:
            logging.error(f"CRÍTICO: Error inesperado: {e}")
            raise SoftwareFJError("Error crítico en el sistema de gestión.") from e

# =================================================================
# 4. INTERFAZ GRÁFICA (Capa de Presentación)
# =================================================================

class AppSoftwareFJ(tk.Tk):
    def __init__(self, gestor):
        super().__init__()
        self.gestor = gestor
        self.title("Software FJ - Gestión de Clientes UNAD")
        self.geometry("600x500")
        self._inicializar_gui()

    def _inicializar_gui(self):
        # Título y Formulario
        tk.Label(self, text="REGISTRO DE CLIENTES", font=("Arial", 12, "bold")).pack(pady=10)
        
        container = tk.Frame(self, padx=20)
        container.pack(fill="x")

        labels = ["ID Cliente", "Nombre", "Email", "Teléfono"]
        self.entries = {}

        for label in labels:
            row = tk.Frame(container)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=15, anchor="w").pack(side="left")
            ent = tk.Entry(row)
            ent.pack(side="right", expand=True, fill="x")
            self.entries[label] = ent

        # Botón Guardar
        tk.Button(self, text="REGISTRAR CLIENTE", bg="#28a745", fg="white", 
                  command=self._ejecutar_accion).pack(pady=15, padx=20, fill="x")

        # Tabla de visualización
        self.tree = ttk.Treeview(self, columns=("ID", "Nombre", "Email", "Tel"), show="headings")
        for col in ("ID", "Nombre", "Email", "Tel"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

    def _ejecutar_accion(self):
        """Manejo robusto de excepciones en la interfaz."""
        try:
            # Captura de datos
            id_v = self.entries["ID Cliente"].get()
            nom_v = self.entries["Nombre"].get()
            em_v = self.entries["Email"].get()
            tel_v = self.entries["Teléfono"].get()

            # Lógica de negocio
            cliente_creado = self.gestor.agregar_cliente(id_v, nom_v, em_v, tel_v)
            
            # Si tiene éxito (Bloque ELSE implícito)
            self.tree.insert("", "end", values=cliente_creado.obtener_info())
            self._limpiar_campos()
            messagebox.showinfo("Éxito", "Cliente registrado correctamente.")

        except ClienteError as e:
            # Captura excepciones personalizadas
            messagebox.showerror("Error de Validación", f"Dato inválido: {e}")
        except SoftwareFJError as e:
            # Captura errores generales del sistema
            messagebox.showwarning("Aviso del Sistema", str(e))
        finally:
            # Registro en consola para depuración
            print(f"Intento de registro finalizado a las {datetime.now()}")

    def _limpiar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

# =================================================================
# 5. PUNTO DE ENTRADA
# =================================================================
if __name__ == "__main__":
    # Iniciar motor lógico y luego la interfaz
    gestor_logico = GestorClientes()
    app = AppSoftwareFJ(gestor_logico)
    app.mainloop()
