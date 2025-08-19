Estoy migrando un proyecto desde el directorio `src_old/` hacia `src/`, implementando una arquitectura limpia. La nueva estructura seguirá este esquema:

```
src/
├── entities/
├── use_cases/
├── application/
├── interface_adapters/
│   ├── controllers/
│   ├── presenters/
│   └── gateways/
└── infrastructure/
```

Quiero que actúes como un auditor experto en arquitectura limpia y me ayudes en el proceso de migración.

1. Analiza los archivos dentro de `src_old/` (asume que puedes ver su estructura y contenido).
2. Indícame qué archivos se pueden migrar directamente, especificando a qué carpeta deberían ir.
3. Para los archivos que **no se pueden migrar directamente**, dime:

   * Qué tipo de refactorización requieren.
   * A qué capa de la arquitectura deberían pertenecer una vez refactorizados.
4. Señala cualquier violación de principios de arquitectura limpia (por ejemplo, dependencias cruzadas incorrectas, lógica de negocio acoplada a infraestructura, etc.).
5. Si detectas código duplicado o responsabilidades mal ubicadas, dame sugerencias para reorganizarlo según la arquitectura propuesta.

Responde con una tabla clara o listas bien estructuradas para que el plan de migración sea fácil de seguir.
