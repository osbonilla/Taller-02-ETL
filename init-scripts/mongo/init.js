// init.js (MongoDB)
// Se ejecuta automaticamente una sola vez, en el primer arranque del
// contenedor, gracias al mecanismo docker-entrypoint-initdb.d de la imagen
// oficial de MongoDB. Se usa getSiblingDB() para apuntar explicitamente a la
// base de datos del taller, sin depender del contexto por defecto del shell.

db = db.getSiblingDB('taller_mongo');

db.inventario.insertMany([
  {
    producto_id: "P00001",
    nombre: "Tecnologia Item 1",
    categoria: "Tecnologia",
    stock: 339,
    precio: 147.13,
    atributos: {
      color: "rojo",
      peso_kg: 3.6,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-04-29T00:00:00Z")
  },
  {
    producto_id: "P00002",
    nombre: "Oficina Item 2",
    categoria: "Oficina",
    stock: 289,
    precio: 569.48,
    atributos: {
      color: "azul",
      peso_kg: 23.49,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-05-15T00:00:00Z")
  },
  {
    producto_id: "P00003",
    nombre: "Oficina Item 3",
    categoria: "Oficina",
    stock: 389,
    precio: 295.15,
    atributos: {
      color: "gris",
      peso_kg: 9.3,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-07-18T00:00:00Z")
  },
  {
    producto_id: "P00004",
    nombre: "Oficina Item 4",
    categoria: "Oficina",
    stock: 265,
    precio: 545.1,
    atributos: {
      color: "azul",
      peso_kg: 11.79,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2025-11-29T00:00:00Z")
  },
  {
    producto_id: "P00005",
    nombre: "Tecnologia Item 5",
    categoria: "Tecnologia",
    stock: 20,
    precio: 588.45,
    atributos: {
      color: "negro",
      peso_kg: 17.62,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-12-27T00:00:00Z")
  },
  {
    producto_id: "P00006",
    nombre: "Hogar Item 6",
    categoria: "Hogar",
    stock: 427,
    precio: 446.44,
    atributos: {
      color: "azul",
      peso_kg: 16.38,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-04-23T00:00:00Z")
  },
  {
    producto_id: "P00007",
    nombre: "Papeleria Item 7",
    categoria: "Papeleria",
    stock: 334,
    precio: 539.44,
    atributos: {
      color: "rojo",
      peso_kg: 6.36,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-07-07T00:00:00Z")
  },
  {
    producto_id: "P00008",
    nombre: "Papeleria Item 8",
    categoria: "Papeleria",
    stock: 207,
    precio: 214.97,
    atributos: {
      color: "azul",
      peso_kg: 19.84,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-12-11T00:00:00Z")
  },
  {
    producto_id: "P00009",
    nombre: "Tecnologia Item 9",
    categoria: "Tecnologia",
    stock: 256,
    precio: 529.81,
    atributos: {
      color: "blanco",
      peso_kg: 5.83,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-09-28T00:00:00Z")
  },
  {
    producto_id: "P00010",
    nombre: "Hogar Item 10",
    categoria: "Hogar",
    stock: 108,
    precio: 94.39,
    atributos: {
      color: "gris",
      peso_kg: 15.09,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-05-06T00:00:00Z")
  },
  {
    producto_id: "P00011",
    nombre: "Oficina Item 11",
    categoria: "Oficina",
    stock: 212,
    precio: 487.65,
    atributos: {
      color: "azul",
      peso_kg: 16.91,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-06-09T00:00:00Z")
  },
  {
    producto_id: "P00012",
    nombre: "Oficina Item 12",
    categoria: "Oficina",
    stock: 302,
    precio: 100.94,
    atributos: {
      color: "negro",
      peso_kg: 6.17,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2025-10-21T00:00:00Z")
  },
  {
    producto_id: "P00013",
    nombre: "Papeleria Item 13",
    categoria: "Papeleria",
    stock: 303,
    precio: 100.87,
    atributos: {
      color: "negro",
      peso_kg: 22.28,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2025-08-03T00:00:00Z")
  },
  {
    producto_id: "P00014",
    nombre: "Tecnologia Item 14",
    categoria: "Tecnologia",
    stock: 85,
    precio: 158.66,
    atributos: {
      color: "rojo",
      peso_kg: 23.96,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-04-18T00:00:00Z")
  },
  {
    producto_id: "P00015",
    nombre: "Papeleria Item 15",
    categoria: "Papeleria",
    stock: 326,
    precio: 16.08,
    atributos: {
      color: "negro",
      peso_kg: 5.49,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-01-28T00:00:00Z")
  },
  {
    producto_id: "P00016",
    nombre: "Deporte Item 16",
    categoria: "Deporte",
    stock: 444,
    precio: 291.59,
    atributos: {
      color: "azul",
      peso_kg: 15.06,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-03-19T00:00:00Z")
  },
  {
    producto_id: "P00017",
    nombre: "Oficina Item 17",
    categoria: "Oficina",
    stock: 319,
    precio: 397.49,
    atributos: {
      color: "blanco",
      peso_kg: 18.13,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-02-12T00:00:00Z")
  },
  {
    producto_id: "P00018",
    nombre: "Deporte Item 18",
    categoria: "Deporte",
    stock: 305,
    precio: 356.4,
    atributos: {
      color: "azul",
      peso_kg: 9.7,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-03-11T00:00:00Z")
  },
  {
    producto_id: "P00019",
    nombre: "Tecnologia Item 19",
    categoria: "Tecnologia",
    stock: 103,
    precio: 316.01,
    atributos: {
      color: "azul",
      peso_kg: 20.68,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-08-09T00:00:00Z")
  },
  {
    producto_id: "P00020",
    nombre: "Tecnologia Item 20",
    categoria: "Tecnologia",
    stock: 90,
    precio: 288.14,
    atributos: {
      color: "rojo",
      peso_kg: 12.63,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-08-06T00:00:00Z")
  },
  {
    producto_id: "P00021",
    nombre: "Tecnologia Item 21",
    categoria: "Tecnologia",
    stock: 246,
    precio: 397.34,
    atributos: {
      color: "azul",
      peso_kg: 13.1,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-09-04T00:00:00Z")
  },
  {
    producto_id: "P00022",
    nombre: "Tecnologia Item 22",
    categoria: "Tecnologia",
    stock: 357,
    precio: 320.24,
    atributos: {
      color: "azul",
      peso_kg: 19.76,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-03-11T00:00:00Z")
  },
  {
    producto_id: "P00023",
    nombre: "Hogar Item 23",
    categoria: "Hogar",
    stock: 301,
    precio: 483.75,
    atributos: {
      color: "azul",
      peso_kg: 3.43,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-06-21T00:00:00Z")
  },
  {
    producto_id: "P00024",
    nombre: "Oficina Item 24",
    categoria: "Oficina",
    stock: 465,
    precio: 516.14,
    atributos: {
      color: "rojo",
      peso_kg: 21.93,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-01-28T00:00:00Z")
  },
  {
    producto_id: "P00025",
    nombre: "Hogar Item 25",
    categoria: "Hogar",
    stock: 96,
    precio: 8.25,
    atributos: {
      color: "rojo",
      peso_kg: 13.11,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-08-31T00:00:00Z")
  },
  {
    producto_id: "P00026",
    nombre: "Tecnologia Item 26",
    categoria: "Tecnologia",
    stock: 192,
    precio: 394.45,
    atributos: {
      color: "azul",
      peso_kg: 9.12,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-01-03T00:00:00Z")
  },
  {
    producto_id: "P00027",
    nombre: "Deporte Item 27",
    categoria: "Deporte",
    stock: 333,
    precio: 353.3,
    atributos: {
      color: "rojo",
      peso_kg: 10.65,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-02-14T00:00:00Z")
  },
  {
    producto_id: "P00028",
    nombre: "Papeleria Item 28",
    categoria: "Papeleria",
    stock: 141,
    precio: 595.12,
    atributos: {
      color: "blanco",
      peso_kg: 10.39,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-10-31T00:00:00Z")
  },
  {
    producto_id: "P00029",
    nombre: "Deporte Item 29",
    categoria: "Deporte",
    stock: 91,
    precio: 225.28,
    atributos: {
      color: "gris",
      peso_kg: 24.71,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-08-25T00:00:00Z")
  },
  {
    producto_id: "P00030",
    nombre: "Hogar Item 30",
    categoria: "Hogar",
    stock: 396,
    precio: 424.77,
    atributos: {
      color: "negro",
      peso_kg: 18.72,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-05-21T00:00:00Z")
  },
  {
    producto_id: "P00031",
    nombre: "Oficina Item 31",
    categoria: "Oficina",
    stock: 51,
    precio: 132.6,
    atributos: {
      color: "gris",
      peso_kg: 20.04,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-10-29T00:00:00Z")
  },
  {
    producto_id: "P00032",
    nombre: "Tecnologia Item 32",
    categoria: "Tecnologia",
    stock: 82,
    precio: 236.52,
    atributos: {
      color: "negro",
      peso_kg: 20.6,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-09-01T00:00:00Z")
  },
  {
    producto_id: "P00033",
    nombre: "Papeleria Item 33",
    categoria: "Papeleria",
    stock: 222,
    precio: 57.44,
    atributos: {
      color: "blanco",
      peso_kg: 9.33,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-02-13T00:00:00Z")
  },
  {
    producto_id: "P00034",
    nombre: "Tecnologia Item 34",
    categoria: "Tecnologia",
    stock: 370,
    precio: 233.67,
    atributos: {
      color: "rojo",
      peso_kg: 16.44,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2025-10-29T00:00:00Z")
  },
  {
    producto_id: "P00035",
    nombre: "Papeleria Item 35",
    categoria: "Papeleria",
    stock: 29,
    precio: 567.7,
    atributos: {
      color: "azul",
      peso_kg: 11.03,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-04-22T00:00:00Z")
  },
  {
    producto_id: "P00036",
    nombre: "Papeleria Item 36",
    categoria: "Papeleria",
    stock: 146,
    precio: 120.87,
    atributos: {
      color: "rojo",
      peso_kg: 17.49,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-08-05T00:00:00Z")
  },
  {
    producto_id: "P00037",
    nombre: "Oficina Item 37",
    categoria: "Oficina",
    stock: 345,
    precio: 26.46,
    atributos: {
      color: "negro",
      peso_kg: 24.39,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-03-03T00:00:00Z")
  },
  {
    producto_id: "P00038",
    nombre: "Hogar Item 38",
    categoria: "Hogar",
    stock: 399,
    precio: 242.66,
    atributos: {
      color: "azul",
      peso_kg: 14.69,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-11-02T00:00:00Z")
  },
  {
    producto_id: "P00039",
    nombre: "Tecnologia Item 39",
    categoria: "Tecnologia",
    stock: 377,
    precio: 423.66,
    atributos: {
      color: "rojo",
      peso_kg: 7.18,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-06-27T00:00:00Z")
  },
  {
    producto_id: "P00040",
    nombre: "Papeleria Item 40",
    categoria: "Papeleria",
    stock: 178,
    precio: 211.75,
    atributos: {
      color: "blanco",
      peso_kg: 15.2,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-02-02T00:00:00Z")
  },
  {
    producto_id: "P00041",
    nombre: "Deporte Item 41",
    categoria: "Deporte",
    stock: 476,
    precio: 245.35,
    atributos: {
      color: "gris",
      peso_kg: 4.46,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-09-02T00:00:00Z")
  },
  {
    producto_id: "P00042",
    nombre: "Tecnologia Item 42",
    categoria: "Tecnologia",
    stock: 286,
    precio: 48.07,
    atributos: {
      color: "gris",
      peso_kg: 23.68,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-01-20T00:00:00Z")
  },
  {
    producto_id: "P00043",
    nombre: "Hogar Item 43",
    categoria: "Hogar",
    stock: 448,
    precio: 325.05,
    atributos: {
      color: "azul",
      peso_kg: 24.15,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-02-23T00:00:00Z")
  },
  {
    producto_id: "P00044",
    nombre: "Deporte Item 44",
    categoria: "Deporte",
    stock: 394,
    precio: 149.75,
    atributos: {
      color: "azul",
      peso_kg: 17.07,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-12-15T00:00:00Z")
  },
  {
    producto_id: "P00045",
    nombre: "Tecnologia Item 45",
    categoria: "Tecnologia",
    stock: 246,
    precio: 74.18,
    atributos: {
      color: "azul",
      peso_kg: 15.88,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-07-15T00:00:00Z")
  },
  {
    producto_id: "P00046",
    nombre: "Oficina Item 46",
    categoria: "Oficina",
    stock: 409,
    precio: 192.86,
    atributos: {
      color: "rojo",
      peso_kg: 13.44,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2025-12-05T00:00:00Z")
  },
  {
    producto_id: "P00047",
    nombre: "Oficina Item 47",
    categoria: "Oficina",
    stock: 147,
    precio: 60.34,
    atributos: {
      color: "negro",
      peso_kg: 13.91,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2025-12-14T00:00:00Z")
  },
  {
    producto_id: "P00048",
    nombre: "Deporte Item 48",
    categoria: "Deporte",
    stock: 160,
    precio: 215.36,
    atributos: {
      color: "blanco",
      peso_kg: 23.68,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-02-08T00:00:00Z")
  },
  {
    producto_id: "P00049",
    nombre: "Deporte Item 49",
    categoria: "Deporte",
    stock: 377,
    precio: 123.8,
    atributos: {
      color: "gris",
      peso_kg: 5.25,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-03-01T00:00:00Z")
  },
  {
    producto_id: "P00050",
    nombre: "Oficina Item 50",
    categoria: "Oficina",
    stock: 428,
    precio: 373.07,
    atributos: {
      color: "negro",
      peso_kg: 3.08,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-05-07T00:00:00Z")
  },
  {
    producto_id: "P00051",
    nombre: "Deporte Item 51",
    categoria: "Deporte",
    stock: 314,
    precio: 8.94,
    atributos: {
      color: "azul",
      peso_kg: 9.34,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-08-03T00:00:00Z")
  },
  {
    producto_id: "P00052",
    nombre: "Deporte Item 52",
    categoria: "Deporte",
    stock: 459,
    precio: 591.29,
    atributos: {
      color: "azul",
      peso_kg: 4.65,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-02-04T00:00:00Z")
  },
  {
    producto_id: "P00053",
    nombre: "Hogar Item 53",
    categoria: "Hogar",
    stock: 203,
    precio: 137.15,
    atributos: {
      color: "negro",
      peso_kg: 13.19,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-05-29T00:00:00Z")
  },
  {
    producto_id: "P00054",
    nombre: "Deporte Item 54",
    categoria: "Deporte",
    stock: 481,
    precio: 326.76,
    atributos: {
      color: "gris",
      peso_kg: 9.9,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2025-08-11T00:00:00Z")
  },
  {
    producto_id: "P00055",
    nombre: "Deporte Item 55",
    categoria: "Deporte",
    stock: 499,
    precio: 76.62,
    atributos: {
      color: "gris",
      peso_kg: 17.26,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2025-09-13T00:00:00Z")
  },
  {
    producto_id: "P00056",
    nombre: "Oficina Item 56",
    categoria: "Oficina",
    stock: 194,
    precio: 350.7,
    atributos: {
      color: "gris",
      peso_kg: 15.36,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2025-12-26T00:00:00Z")
  },
  {
    producto_id: "P00057",
    nombre: "Oficina Item 57",
    categoria: "Oficina",
    stock: 280,
    precio: 161.4,
    atributos: {
      color: "azul",
      peso_kg: 23.97,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-02-08T00:00:00Z")
  },
  {
    producto_id: "P00058",
    nombre: "Hogar Item 58",
    categoria: "Hogar",
    stock: 94,
    precio: 301.77,
    atributos: {
      color: "azul",
      peso_kg: 17.55,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-03-26T00:00:00Z")
  },
  {
    producto_id: "P00059",
    nombre: "Hogar Item 59",
    categoria: "Hogar",
    stock: 437,
    precio: 243.35,
    atributos: {
      color: "blanco",
      peso_kg: 14.33,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-09-20T00:00:00Z")
  },
  {
    producto_id: "P00060",
    nombre: "Oficina Item 60",
    categoria: "Oficina",
    stock: 416,
    precio: 64.42,
    atributos: {
      color: "blanco",
      peso_kg: 13.93,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-02-07T00:00:00Z")
  },
  {
    producto_id: "P00061",
    nombre: "Oficina Item 61",
    categoria: "Oficina",
    stock: 74,
    precio: 481.02,
    atributos: {
      color: "azul",
      peso_kg: 20.16,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-05-12T00:00:00Z")
  },
  {
    producto_id: "P00062",
    nombre: "Deporte Item 62",
    categoria: "Deporte",
    stock: 255,
    precio: 85.01,
    atributos: {
      color: "azul",
      peso_kg: 7.57,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-01-03T00:00:00Z")
  },
  {
    producto_id: "P00063",
    nombre: "Papeleria Item 63",
    categoria: "Papeleria",
    stock: 24,
    precio: 242.05,
    atributos: {
      color: "negro",
      peso_kg: 5.47,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-05-01T00:00:00Z")
  },
  {
    producto_id: "P00064",
    nombre: "Deporte Item 64",
    categoria: "Deporte",
    stock: 429,
    precio: 379.77,
    atributos: {
      color: "gris",
      peso_kg: 6.57,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2025-09-21T00:00:00Z")
  },
  {
    producto_id: "P00065",
    nombre: "Papeleria Item 65",
    categoria: "Papeleria",
    stock: 285,
    precio: 559.45,
    atributos: {
      color: "gris",
      peso_kg: 0.59,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-02-17T00:00:00Z")
  },
  {
    producto_id: "P00066",
    nombre: "Hogar Item 66",
    categoria: "Hogar",
    stock: 444,
    precio: 409.35,
    atributos: {
      color: "rojo",
      peso_kg: 14.44,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-04-04T00:00:00Z")
  },
  {
    producto_id: "P00067",
    nombre: "Oficina Item 67",
    categoria: "Oficina",
    stock: 399,
    precio: 174.34,
    atributos: {
      color: "rojo",
      peso_kg: 12.24,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2025-12-27T00:00:00Z")
  },
  {
    producto_id: "P00068",
    nombre: "Tecnologia Item 68",
    categoria: "Tecnologia",
    stock: 195,
    precio: 370.13,
    atributos: {
      color: "blanco",
      peso_kg: 21.72,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2025-09-10T00:00:00Z")
  },
  {
    producto_id: "P00069",
    nombre: "Deporte Item 69",
    categoria: "Deporte",
    stock: 323,
    precio: 369.32,
    atributos: {
      color: "negro",
      peso_kg: 2.07,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2025-10-26T00:00:00Z")
  },
  {
    producto_id: "P00070",
    nombre: "Oficina Item 70",
    categoria: "Oficina",
    stock: 160,
    precio: 193.54,
    atributos: {
      color: "gris",
      peso_kg: 15.17,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-01-22T00:00:00Z")
  },
  {
    producto_id: "P00071",
    nombre: "Hogar Item 71",
    categoria: "Hogar",
    stock: 454,
    precio: 269.71,
    atributos: {
      color: "rojo",
      peso_kg: 13.07,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2025-11-27T00:00:00Z")
  },
  {
    producto_id: "P00072",
    nombre: "Deporte Item 72",
    categoria: "Deporte",
    stock: 85,
    precio: 114.41,
    atributos: {
      color: "blanco",
      peso_kg: 18.22,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2026-08-18T00:00:00Z")
  },
  {
    producto_id: "P00073",
    nombre: "Tecnologia Item 73",
    categoria: "Tecnologia",
    stock: 107,
    precio: 104.31,
    atributos: {
      color: "negro",
      peso_kg: 1.69,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-06-17T00:00:00Z")
  },
  {
    producto_id: "P00074",
    nombre: "Papeleria Item 74",
    categoria: "Papeleria",
    stock: 27,
    precio: 20.69,
    atributos: {
      color: "rojo",
      peso_kg: 19.15,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2025-11-01T00:00:00Z")
  },
  {
    producto_id: "P00075",
    nombre: "Tecnologia Item 75",
    categoria: "Tecnologia",
    stock: 134,
    precio: 372.77,
    atributos: {
      color: "azul",
      peso_kg: 7.8,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-07-02T00:00:00Z")
  },
  {
    producto_id: "P00076",
    nombre: "Hogar Item 76",
    categoria: "Hogar",
    stock: 226,
    precio: 377.76,
    atributos: {
      color: "rojo",
      peso_kg: 20.98,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-05-26T00:00:00Z")
  },
  {
    producto_id: "P00077",
    nombre: "Tecnologia Item 77",
    categoria: "Tecnologia",
    stock: 339,
    precio: 217.32,
    atributos: {
      color: "azul",
      peso_kg: 11.73,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-12-27T00:00:00Z")
  },
  {
    producto_id: "P00078",
    nombre: "Hogar Item 78",
    categoria: "Hogar",
    stock: 280,
    precio: 269.68,
    atributos: {
      color: "rojo",
      peso_kg: 14.98,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-04-21T00:00:00Z")
  },
  {
    producto_id: "P00079",
    nombre: "Deporte Item 79",
    categoria: "Deporte",
    stock: 268,
    precio: 385.67,
    atributos: {
      color: "gris",
      peso_kg: 12.09,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-01-08T00:00:00Z")
  },
  {
    producto_id: "P00080",
    nombre: "Tecnologia Item 80",
    categoria: "Tecnologia",
    stock: 226,
    precio: 188.18,
    atributos: {
      color: "gris",
      peso_kg: 3.98,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2025-10-20T00:00:00Z")
  },
  {
    producto_id: "P00081",
    nombre: "Tecnologia Item 81",
    categoria: "Tecnologia",
    stock: 267,
    precio: 490.15,
    atributos: {
      color: "gris",
      peso_kg: 7.24,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-05-22T00:00:00Z")
  },
  {
    producto_id: "P00082",
    nombre: "Tecnologia Item 82",
    categoria: "Tecnologia",
    stock: 352,
    precio: 553.64,
    atributos: {
      color: "gris",
      peso_kg: 0.33,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2025-08-31T00:00:00Z")
  },
  {
    producto_id: "P00083",
    nombre: "Hogar Item 83",
    categoria: "Hogar",
    stock: 305,
    precio: 142.57,
    atributos: {
      color: "rojo",
      peso_kg: 9.4,
      marca: "SportPro"
    },
    fecha_ingreso: ISODate("2026-08-31T00:00:00Z")
  },
  {
    producto_id: "P00084",
    nombre: "Papeleria Item 84",
    categoria: "Papeleria",
    stock: 223,
    precio: 239.88,
    atributos: {
      color: "azul",
      peso_kg: 20.73,
      marca: "OfiMax"
    },
    fecha_ingreso: ISODate("2026-05-01T00:00:00Z")
  },
  {
    producto_id: "P00085",
    nombre: "Hogar Item 85",
    categoria: "Hogar",
    stock: 40,
    precio: 256.23,
    atributos: {
      color: "rojo",
      peso_kg: 19.14,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2026-03-03T00:00:00Z")
  },
  {
    producto_id: "P00086",
    nombre: "Hogar Item 86",
    categoria: "Hogar",
    stock: 145,
    precio: 390.83,
    atributos: {
      color: "azul",
      peso_kg: 4.78,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-02-08T00:00:00Z")
  },
  {
    producto_id: "P00087",
    nombre: "Oficina Item 87",
    categoria: "Oficina",
    stock: 69,
    precio: 177.31,
    atributos: {
      color: "rojo",
      peso_kg: 11.37,
      marca: "PaperCo"
    },
    fecha_ingreso: ISODate("2025-09-16T00:00:00Z")
  },
  {
    producto_id: "P00088",
    nombre: "Deporte Item 88",
    categoria: "Deporte",
    stock: 96,
    precio: 195.78,
    atributos: {
      color: "negro",
      peso_kg: 24.25,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-05-10T00:00:00Z")
  },
  {
    producto_id: "P00089",
    nombre: "Oficina Item 89",
    categoria: "Oficina",
    stock: 497,
    precio: 65.85,
    atributos: {
      color: "blanco",
      peso_kg: 17.91,
      marca: "NovaTech"
    },
    fecha_ingreso: ISODate("2026-02-08T00:00:00Z")
  },
  {
    producto_id: "P00090",
    nombre: "Oficina Item 90",
    categoria: "Oficina",
    stock: 46,
    precio: 94.66,
    atributos: {
      color: "blanco",
      peso_kg: 8.61,
      marca: "HomeLine"
    },
    fecha_ingreso: ISODate("2025-08-18T00:00:00Z")
  }
]);

db.inventario.createIndex({ producto_id: 1 }, { unique: true });
