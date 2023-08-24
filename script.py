import sys
import logging
import boto3
import pandas as pd


def lambda_list_comparation(event, context):

     # Gera logs de execução
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Variáveis Globais
    BUCKET_NAME = os.environ.get('BUCKET_NAME')
    CSV_BACKUP = os.environ.get('CSV_BACKUP')
    LIST_PROCESSED = os.environ.get('LIST_PROCESSED')
    LIST_UPDATED = os.environ.get('LIST_UPDATED')

    # Conexão com AWS S3
    try:
        s3 = boto3.client('s3')
    except Exception as e:
        logger.error(f"Erro na conexão com o S3: {e}")
        sys.exit()

    # Faz o download das listas CSV_BACKUP - LIST_PROCESSED AWS S3
    try:
        s3.download_file(BUCKET_NAME, f'list/{CSV_BACKUP}', f'/tmp/{CSV_BACKUP}')
        s3.download_file(BUCKET_NAME, f'list/{LIST_PROCESSED}', f'/tmp/{LIST_PROCESSED}')
        logger.info("Sucesso: Download das Listas")
    except Exception as e:
        logger.error(f"Erro ao fazer o download das listas: {e}")
        sys.exit()

    # Carrega as listas CSV CSV_BACKUP - LIST_PROCESSED
    try:
        list_bkp = pd.read_csv(f'/tmp/{CSV_BACKUP}', header=None)
        list_processed = pd.read_csv(f'/tmp/{LIST_PROCESSED}', header=None)
        logger.info("Sucesso: carregamento das listas")
    except Exception as e:
        logger.error(f"Erro no carregamento das listas CSV: {e}")
        sys.exit()

    # Identifica os índices das linhas em comum nas duas listas
    try:
        indices_comuns = list_bkp[list_bkp.iloc[:, 0].isin(list_processed.iloc[:, 0])].index
        logger.info("Sucesso: identificação linhas em comuns")
    except Exception as e:
        logger.error(f"Erro ao identificar índices das linhas em comum: {e}")
        sys.exit()

    # Remove as linhas em comum da lista CSV_BACKUP
    try:
        list_bkp_sem_comuns = list_bkp.drop(indices_comuns)
        logger.info("Sucesso: removido as linhas em comuns da lista CSV_BACKUP")
    except Exception as e:
        logger.error(f"Erro ao remover as linhas em comum da CSV_BACKUP: {e}")
        sys.exit()

    # Salva a CSV_BACKUP atualizada em um novo arquivo CSV
    try:
        list_bkp_sem_comuns.to_csv(f'/tmp/{LIST_UPDATED}', header=None, index=False)
        logger.info("Sucesso: Lista CSV_BACKUP atualizada exportada")
    except Exception as e:
        logger.error(f"Erro ao salvar a lista atualizada em um novo arquivo CSV: {e}")
        sys.exit()

    # Faz o upload da CSV_BACKUP atualizada de volta para o S3
    try:
        s3.upload_file(f'/tmp/{LIST_UPDATED}', BUCKET_NAME, f'list/{CSV_BACKUP}')
        logger.info("Sucesso: Lista CSV_BACKUP atualizada")
    except Exception as e:
        logger.error(f"Erro ao fazer upload da  atualizada para o S3: {e}")
        sys.exit()
    
    # 1 - Realiza o download das duas listas
    # 2 - Compara a lista de backup com a lista dos arquivos já processados 
    # 3 - Remove os arquivos já processados da lista de backup 
    # 4 - Realiza o upload da lista atualizada para o S3