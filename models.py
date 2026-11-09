from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey,select
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, declarative_base
from sqlalchemy.sql import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# criar a conexão com o banco

engine = create_engine('sqlite:///banco.db', echo=True)

Base = declarative_base()

db_session = scoped_session(sessionmaker(bind=engine))

class Usuario(Base, UserMixin):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(DateTime, nullable=False, default=func.now())

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255))
    estoque_atual = Column(Integer,default=0)
    estoque_minimo = Column(Integer,default=5)
    criado_em = Column(DateTime, nullable=False, default=func.now())

    movimentacao = relationship("Movimentacao", back_populates="produto")

class Movimentacao(Base):
    __tablename__ = 'movimentacoes'
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    quantidade = Column(Integer, nullable=False)
    data_operacao = Column(DateTime, nullable=False)
    criado_em = Column(DateTime, nullable=False, default=func.now())

    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    produto_id = Column(Integer, ForeignKey('produtos.id'))

    produto = relationship("Produto", back_populates="movimentacao")
    usuario = relationship("Usuario")


def inicializar_banco():
    Base.metadata.create_all(engine)
    if not db_session.execute(select(Usuario.id)).scalar():
        admin = Usuario(nome='admin', email='adm@email.com')
        admin.set_password('123')
        db_session.add(admin)
        db_session.commit()

if __name__ == '__main__':
    inicializar_banco()
    print("Base de dados inicializada com sucesso!")

