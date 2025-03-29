import singlestoredb as s2

with s2.connect(
    host="svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com",
    port=3333,
    user="guilherme", 
    password="HDps2V1ziGncqV5BWSEePEROjKWMUzIt",
    database="db_smartnurse"
) as conn:

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM fake_patients_en ORDER BY id ASC LIMIT 5;")
        results = cur.fetchall()
        
    for pacient in results:
        for parameter in pacient:
            print(parameter)
            print("\n")
        print("-" * 50 + "\n")