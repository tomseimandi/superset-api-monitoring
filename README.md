# Dashboard de monitoring pour API de codification

## Contexte

Des logs générés par l'API de codification ou par un client sont poussés sur s3. Un ETL (parser léger) tourne tous les jours pour formatter les logs de la journée au format .parquet.
On suppose donc qu'on dispose des données de logs au format .parquet partitionnés par jour.

## Stack

Pour créer un dashboard de monitoring à partir de ces logs, on utilise Apache Superset avec une base de données DuckDB.
Une première configuration simple possible (sur le SSP Cloud) est d'ajouter une base de données, de choisir DuckDB dans la liste de base de données prises en charge, puis de renseigner `duckdb:///:memory:` dans le champ `SQLALCHEMY URI`. Valider la connexion puis dans le SQL Lab, exécuter la commande `INSTALL httpfs;`. Puis retourner éditer la base de données DuckDB créée : dans l'onglet "ADVANCED", cocher la case "Allow DML" puis dans "Other", rajouter dans "ENGINE PARAMETERS" le json suivant :

```
{"connect_args": {
    "preload_extensions": ["httpfs"],
    "config": {
        "s3_endpoint": "minio.lab.sspcloud.fr",
        "s3_access_key_id": "<YOUR_ACCESS_KEY>",
        "s3_secret_access_key": "<YOUR_SECRET_KEY>",
        "s3_session_token": "<YOUR TOKEN>",
        "s3_url_style":"path"
    }
}}
```

## Création d'un dashboard

Si la connexion fonctionne, il est alors possible de créer un dashboard, à partir de "Charts" elles-mêmes créées à partir de requêtes SQL. Par exemple, pour récupérer toutes les données de log, en supposant qu'elles sont stockées dans le bucket `projet-ape` et au path `log_files/dashboard/` (avec un partitionnement par jour), exécuter la commande :

```
SELECT count(*) FROM read_parquet('s3://projet-ape/log_files/dashboard/*/daily_logs_0.parquet', HIVE_PARTITIONING = 1);
```

Les "Charts" se font ensuite en clique-bouton, avec possibilité d'introduire des calculs ad-hoc en SQL.

## Exemple de requêtes

Pour récupérer les 20 derniers jours de log (la requête n'est sûrement pas optimale...) :

```
SELECT * from read_parquet('s3://projet-ape/log_files/dashboard/*/daily_logs_0.parquet', HIVE_PARTITIONING = 1) WHERE date IN (
  SELECT DISTINCT(date) from read_parquet('s3://projet-ape/log_files/dashboard/*/daily_logs_0.parquet', HIVE_PARTITIONING = 1) ORDER BY date desc LIMIT 20
);
```

## Stack alternative

Une stack plus complexe est potentiellement envisageable si on a besoin de scaler, avec l'utilisation d'un moteur de calcul distribué, Trino.
On pourrait par exemple utiliser la stack **Superset** :rightarrow: **Trino** :rightarrow: **Hive**. Pour cette stack il faut avoir les metadatas des fichiers parquets renseignés en plus dans un Hive Metastore. Le Metastore est découvert automatiquement par Trino sur le SSP Cloud (fichier `/opt/hive/conf/hive-site.xml`). On ajoute une base de données Trino sur Superset avec l'URI `trino://<TRINO_USER>:<TRINO_PASSWORD>@<TRINO_HOST>:><PORT>/hive/default`. Par contre pour le moment bug car je ne parviens pas à configurer le connecteur Hive pour autoriser la lecture récursive (nécessaire pour lire les partitions) - voir le notebook.


