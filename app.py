from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)

# Chemins et configuration sensibles
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'supermarche.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nom_complet = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='utilisateur')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    produits = db.relationship('Produit', backref='categorie', lazy=True)

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    designation = db.Column(db.String(200), nullable=False)
    famille = db.Column(db.String(100), nullable=False)
    unite = db.Column(db.String(20), nullable=False)
    prix_total = db.Column(db.Float, nullable=False, default=0.0)
    prix_boutique = db.Column(db.Float, nullable=False, default=0.0)
    prix_magasin1 = db.Column(db.Float, nullable=False, default=0.0)
    prix_magasin2 = db.Column(db.Float, nullable=False, default=0.0)
    prix_magasin3 = db.Column(db.Float, nullable=False, default=0.0)
    stock_affiche = db.Column(db.Integer, nullable=False, default=0)
    stock_minimal = db.Column(db.Integer, nullable=False, default=0)
    stock_revient = db.Column(db.Integer, nullable=False, default=0)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'), nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin role decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('Accès refusé. Privilèges administrateur requis.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['nom_complet'] = user.nom_complet
            session['user_role'] = user.role
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve les images du dossier local images/"""
    images_dir = os.path.join(BASE_DIR, 'images')
    return send_from_directory(images_dir, filename)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/produits')
@login_required
def liste_produits():
    search = request.args.get('search', '')
    famille_filter = request.args.get('famille', '')
    stock_filter = request.args.get('stock_filter', '')
    
    query = Produit.query
    
    if search:
        query = query.filter(
            (Produit.code.contains(search)) | 
            (Produit.designation.contains(search))
        )
    
    if famille_filter:
        query = query.filter(Produit.famille == famille_filter)
    
    if stock_filter == 'en_stock':
        query = query.filter(Produit.stock_affiche > 0)
    elif stock_filter == 'rupture':
        query = query.filter(Produit.stock_affiche <= Produit.stock_minimal)
    
    produits = query.all()
    familles = db.session.query(Produit.famille).distinct().all()
    familles = [f[0] for f in familles]
    
    return render_template('produits.html', produits=produits, familles=familles, 
                         search=search, famille_filter=famille_filter, stock_filter=stock_filter)

@app.route('/produit/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau_produit():
    if request.method == 'POST':
        produit = Produit(
            code=request.form['code'],
            designation=request.form['designation'],
            famille=request.form['famille'],
            unite=request.form['unite'],
            prix_total=float(request.form['prix_total']),
            prix_boutique=float(request.form['prix_boutique']),
            prix_magasin1=float(request.form['prix_magasin1']),
            prix_magasin2=float(request.form['prix_magasin2']),
            prix_magasin3=float(request.form['prix_magasin3']),
            stock_affiche=int(request.form['stock_affiche']),
            stock_minimal=int(request.form['stock_minimal']),
            stock_revient=int(request.form['stock_revient'])
        )
        
        try:
            db.session.add(produit)
            db.session.commit()
            flash('Produit ajouté avec succès!', 'success')
            return redirect(url_for('liste_produits'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'ajout du produit.', 'error')
    
    return render_template('nouveau_produit.html')

@app.route('/produit/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_produit(id):
    produit = Produit.query.get_or_404(id)
    
    if request.method == 'POST':
        produit.code = request.form['code']
        produit.designation = request.form['designation']
        produit.famille = request.form['famille']
        produit.unite = request.form['unite']
        produit.prix_total = float(request.form['prix_total'])
        produit.prix_boutique = float(request.form['prix_boutique'])
        produit.prix_magasin1 = float(request.form['prix_magasin1'])
        produit.prix_magasin2 = float(request.form['prix_magasin2'])
        produit.prix_magasin3 = float(request.form['prix_magasin3'])
        produit.stock_affiche = int(request.form['stock_affiche'])
        produit.stock_minimal = int(request.form['stock_minimal'])
        produit.stock_revient = int(request.form['stock_revient'])
        
        try:
            db.session.commit()
            flash('Produit modifié avec succès!', 'success')
            return redirect(url_for('liste_produits'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la modification du produit.', 'error')
    
    return render_template('modifier_produit.html', produit=produit)

@app.route('/produit/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_produit(id):
    produit = Produit.query.get_or_404(id)
    
    try:
        db.session.delete(produit)
        db.session.commit()
        flash('Produit supprimé avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression du produit.', 'error')
    
    return redirect(url_for('liste_produits'))

@app.route('/produits/vider-tout', methods=['POST'])
@login_required
def vider_tous_produits():
    """Supprimer tous les produits"""
    try:
        nb_produits = Produit.query.count()
        Produit.query.delete()
        db.session.commit()
        flash(f'{nb_produits} produits supprimés avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression des produits.', 'error')
    
    return redirect(url_for('liste_produits'))

@app.route('/produits/supprimer-selection', methods=['POST'])
@login_required
def supprimer_selection_produits():
    """Supprimer les produits sélectionnés"""
    produits_ids = request.form.getlist('produits_selection')
    
    if not produits_ids:
        flash('Aucun produit sélectionné', 'error')
        return redirect(url_for('liste_produits'))
    
    try:
        nb_supprimes = 0
        for produit_id in produits_ids:
            produit = Produit.query.get(produit_id)
            if produit:
                db.session.delete(produit)
                nb_supprimes += 1
        
        db.session.commit()
        flash(f'{nb_supprimes} produits supprimés avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression des produits.', 'error')
    
    return redirect(url_for('liste_produits'))

@app.route('/facturation')
@login_required
def facturation():
    return render_template('facturation.html')

@app.route('/stock')
@login_required
def gestion_stock():
    produits_faible_stock = Produit.query.filter(
        Produit.stock_affiche <= Produit.stock_minimal
    ).all()
    return render_template('stock.html', produits_faible_stock=produits_faible_stock)

@app.route('/rapports')
@admin_required
def rapports():
    total_produits = Produit.query.count()
    produits_rupture = Produit.query.filter(Produit.stock_affiche <= Produit.stock_minimal).count()
    valeur_stock = db.session.query(db.func.sum(Produit.prix_total * Produit.stock_affiche)).scalar() or 0
    
    stats = {
        'total_produits': total_produits,
        'produits_rupture': produits_rupture,
        'valeur_stock': valeur_stock
    }
    
    return render_template('rapports.html', stats=stats)

@app.route('/api/alertes-stock')
@login_required
def api_alertes_stock():
    """API endpoint pour récupérer les alertes de stock"""
    produits_faible_stock = Produit.query.filter(
        Produit.stock_affiche <= Produit.stock_minimal
    ).limit(5).all()
    
    alertes = []
    for produit in produits_faible_stock:
        alertes.append({
            'code': produit.code,
            'designation': produit.designation,
            'stock_affiche': produit.stock_affiche,
            'stock_minimal': produit.stock_minimal
        })
    
    return jsonify(alertes)

def init_db():
    """Initialize database structure only, preserve existing data"""
    db.create_all()
    
    # Check if users exist, if not create default admin user
    if User.query.first() is None:
        print("👤 Création de l'utilisateur administrateur par défaut...")
        admin_user = User(
            username='admin',
            nom_complet='Administrateur',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Add a regular user too
        user = User(
            username='user',
            nom_complet='Utilisateur',
            role='utilisateur'
        )
        user.set_password('user123')
        db.session.add(user)
        
        db.session.commit()
        print("✓ Utilisateurs créés: admin/admin123 et user/user123")
    
    # Only create basic categories, no default products
    if Categorie.query.first() is None:
        print("📊 Création des catégories de base...")
        categories = [
            Categorie(nom='ELECTRICITE'),
            Categorie(nom='MENAGE'),
            Categorie(nom='PLOMBERIE')
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        try:
            db.session.commit()
            print("✓ Catégories de base créées")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Erreur lors de la création des catégories: {e}")
    
    print("✓ Base de données initialisée - aucun produit par défaut")

# Initialisation automatique de la base (utile pour Render et le dev)
if os.environ.get("AUTO_INIT_DB", "1") == "1":
    with app.app_context():
        init_db()

if __name__ == '__main__':
    print("🚀 Démarrage de GbGescom - Gestion de Supermarché")
    print("=" * 50)
    print("📍 URL: http://localhost:5000")
    print("🔧 Mode: Développement")
    print("📊 Base de données: SQLite")
    print("=" * 50)
    
    print("\n🌐 Lancement du serveur web...")
    print("Appuyez sur Ctrl+C pour arrêter l'application")
    app.run(debug=True, host='127.0.0.1', port=5000)
