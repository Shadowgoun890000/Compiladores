// Ejemplo de TypeScript con interfaces y tipos
interface Usuario {
    id: number;
    nombre: string;
    email: string;
    edad?: number;
}

type TipoRol = 'admin' | 'usuario' | 'invitado';

class GestorUsuarios {
    private usuarios: Map<number, Usuario>;

    constructor() {
        this.usuarios = new Map();
    }

    agregarUsuario(usuario: Usuario, rol: TipoRol): boolean {
        if (this.usuarios.has(usuario.id)) {
            return false;
        }

        this.usuarios.set(usuario.id, usuario);
        return true;
    }

    obtenerUsuario(id: number): Usuario | undefined {
        return this.usuarios.get(id);
    }

    actualizarUsuario(id: number, datos: Partial<Usuario>): boolean {
        const usuario = this.usuarios.get(id);
        if (!usuario) {
            return false;
        }

        this.usuarios.set(id, { ...usuario, ...datos });
        return true;
    }
}

// Uso del gestor
const gestor = new GestorUsuarios();

const nuevoUsuario: Usuario = {
    id: 1,
    nombre: "Juan Pérez",
    email: "juan@example.com",
    edad: 25
};