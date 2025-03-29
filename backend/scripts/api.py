import singlestoredb as s2

with s2.connect(
    host="svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com",
    port=3333,
    user="guilherme", 
    password="R9oTOoFIvdAqFg0Yox5jqd4PzF4hQ7rP",
    database="db_smartnurse"
) as conn:

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM fake_patients_en ORDER BY id ASC LIMIT 5;")
        resultados = cur.fetchone()
        print(resultados)
        
    # for paciente in resultados:
    #     print(paciente)
    #     print("-" * 50 + "\n")