import numpy as np
import joblib
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score


class TrainGenreModel:

    @staticmethod
    def get_customer_features(customer_id, connection):
        """
        Extract features for a specific customer from the database.
        Returns a dictionary with the customer's features or None if customer not found.
        """
        try:
            with connection.cursor() as cursor:
                # Query to get customer features - same logic as training
                query = """
                WITH customer_genre_purchases AS (
                    SELECT 
                        c.customer_id,
                        g.name as genre_name,
                        COUNT(*) as purchase_count,
                        SUM(il.quantity) as total_quantity,
                        SUM(il.unit_price * il.quantity) as total_spent_on_genre
                    FROM customer c
                    JOIN invoice i ON c.customer_id = i.customer_id
                    JOIN invoice_line il ON i.invoice_id = il.invoice_id
                    JOIN track t ON il.track_id = t.track_id
                    JOIN genre g ON t.genre_id = g.genre_id
                    WHERE c.customer_id = %s
                    GROUP BY c.customer_id, g.name
                ),
                customer_totals AS (
                    SELECT 
                        customer_id,
                        SUM(total_spent_on_genre) as total_spent,
                        SUM(total_quantity) as total_tracks_bought
                    FROM customer_genre_purchases
                    GROUP BY customer_id
                ),
                customer_preferred_genre AS (
                    SELECT 
                        cgp.customer_id,
                        cgp.genre_name,
                        cgp.total_spent_on_genre,
                        ct.total_spent,
                        ct.total_tracks_bought,
                        (cgp.total_spent_on_genre / ct.total_spent) as genre_spending_ratio,
                        ROW_NUMBER() OVER (PARTITION BY cgp.customer_id ORDER BY cgp.total_spent_on_genre DESC) as genre_rank
                    FROM customer_genre_purchases cgp
                    JOIN customer_totals ct ON cgp.customer_id = ct.customer_id
                )
                SELECT 
                    customer_id,
                    total_spent,
                    total_tracks_bought,
                    genre_spending_ratio
                FROM customer_preferred_genre
                WHERE genre_rank = 1
                AND customer_id = %s;
                """
                
                cursor.execute(query, (customer_id, customer_id))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'customer_id': row[0],
                        'total_spent': float(row[1]) if row[1] else 0.0,
                        'total_tracks_bought': int(row[2]) if row[2] else 0,
                        'genre_spending_ratio': float(row[3]) if row[3] else 0.0
                    }
                else:
                    # Customer exists but has no purchases - return default values
                    cursor.execute("SELECT customer_id FROM customer WHERE customer_id = %s", (customer_id,))
                    if cursor.fetchone():
                        return {
                            'customer_id': customer_id,
                            'total_spent': 0.0,
                            'total_tracks_bought': 0,
                            'genre_spending_ratio': 0.0
                        }
                    else:
                        return None  # Customer doesn't exist
                        
        except Exception as e:
            print(f"Error extracting customer features: {e}")
            return None

    @staticmethod
    def entrenarModeloGenero():
        """
        Trains a classification model to predict customer music genre preferences
        based on their purchase history and demographic data.
        """
        
        # Load environment variables
        load_dotenv("/app/.env")
        USER = os.getenv("SUPABASE_USER")
        PASSWORD = os.getenv("SUPABASE_PASSWORD")
        HOST = os.getenv("SUPABASE_HOST")
        PORT = os.getenv("SUPABASE_PORT")
        DBNAME = os.getenv("SUPABASE_DBNAME")
        
        if PORT is None:
            print("Error: Environment variables not loaded")
            return
        else:
            print("Environment variables loaded successfully")

        try:
            with psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            ) as connection:
                with connection.cursor() as cursor:
                    # SQL query to extract customer features and their most purchased genre
                    query = """
                    WITH customer_genre_purchases AS (
                        SELECT 
                            c.customer_id,
                            g.name as genre_name,
                            COUNT(*) as purchase_count,
                            SUM(il.quantity) as total_quantity,
                            SUM(il.unit_price * il.quantity) as total_spent_on_genre
                        FROM customer c
                        JOIN invoice i ON c.customer_id = i.customer_id
                        JOIN invoice_line il ON i.invoice_id = il.invoice_id
                        JOIN track t ON il.track_id = t.track_id
                        JOIN genre g ON t.genre_id = g.genre_id
                        GROUP BY c.customer_id, g.name
                    ),
                    customer_totals AS (
                        SELECT 
                            customer_id,
                            SUM(total_spent_on_genre) as total_spent,
                            SUM(total_quantity) as total_tracks_bought
                        FROM customer_genre_purchases
                        GROUP BY customer_id
                    ),
                    customer_preferred_genre AS (
                        SELECT 
                            cgp.customer_id,
                            cgp.genre_name,
                            cgp.total_spent_on_genre,
                            ct.total_spent,
                            ct.total_tracks_bought,
                            (cgp.total_spent_on_genre / ct.total_spent) as genre_spending_ratio,
                            ROW_NUMBER() OVER (PARTITION BY cgp.customer_id ORDER BY cgp.total_spent_on_genre DESC) as genre_rank
                        FROM customer_genre_purchases cgp
                        JOIN customer_totals ct ON cgp.customer_id = ct.customer_id
                    )
                    SELECT 
                        customer_id,
                        genre_name as preferred_genre,
                        total_spent,
                        total_tracks_bought,
                        genre_spending_ratio
                    FROM customer_preferred_genre
                    WHERE genre_rank = 1
                    AND total_spent > 0;
                    """
                    
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    print(f"Retrieved {len(rows)} customer records for training")

        except Exception as e:
            print(f"Error connecting to database or executing query: {e}")
            return
        
        if not rows:
            print("No customer data retrieved. Aborting training.")
            return

        # Convert to DataFrame for easier manipulation
        columns = ['customer_id', 'preferred_genre', 'total_spent', 'total_tracks_bought', 'genre_spending_ratio']
        df = pd.DataFrame(rows, columns=columns)
        
        print(f"Sample data:\n{df.head()}")
        print(f"\nGenre distribution:\n{df['preferred_genre'].value_counts()}")
        
        # Prepare features for training
        # We'll use total_spent, total_tracks_bought, genre_spending_ratio
        
        # Encode categorical variables (only genre for target)
        le_genre = LabelEncoder()
        
        df['genre_encoded'] = le_genre.fit_transform(df['preferred_genre'])
        
        # Features (X) and target (y)
        feature_columns = ['total_spent', 'total_tracks_bought', 'genre_spending_ratio']
        X = df[feature_columns].values
        y = df['genre_encoded'].values
        
        # Check class distribution and filter out classes with too few samples
        from collections import Counter
        class_counts = Counter(y)
        min_samples_per_class = 2
        
        # Filter out classes with less than min_samples_per_class
        valid_classes = [cls for cls, count in class_counts.items() if count >= min_samples_per_class]
        
        if len(valid_classes) < len(class_counts):
            print("Filtering out genres with insufficient samples:")
            for cls, count in class_counts.items():
                if count < min_samples_per_class:
                    genre_name = le_genre.inverse_transform([cls])[0]
                    print(f"  - {genre_name}: {count} samples (minimum required: {min_samples_per_class})")
            
            # Filter the data to include only valid classes
            valid_mask = np.isin(y, valid_classes)
            X = X[valid_mask]
            y = y[valid_mask]
            
            print(f"Training with {len(valid_classes)} genres and {len(X)} samples")
        
        # Split the data - use stratify only if we have enough samples per class
        if len(X) >= 10 and all(class_counts[cls] >= 2 for cls in np.unique(y)):
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            # Don't use stratify if we have too few samples
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        
        # Train the model
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nModel Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        
        # Get the actual classes used in training (after filtering)
        unique_classes_in_training = np.unique(y_train)
        actual_genre_names = [le_genre.inverse_transform([cls])[0] for cls in unique_classes_in_training]
        
        print(classification_report(y_test, y_pred, 
                                  target_names=actual_genre_names,
                                  labels=unique_classes_in_training))
        
        # Save the model and encoders
        model_data = {
            'model': model,
            'label_encoders': {
                'genre': le_genre
            },
            'feature_columns': feature_columns,
            'genre_classes': le_genre.classes_
        }
        
        model_path = os.getenv("MODELO_GENERO_ENTRENADO", "/app/assets/modelo_genero_entrenado.pkl")
        joblib.dump(model_data, model_path)
        
        print(f"Genre classification model trained and saved to {model_path}")
        
        # Print feature importance
        feature_names = ['Total Spent', 'Total Tracks', 'Genre Ratio']
        importances = model.feature_importances_
        
        print("\nFeature Importance:")
        for name, importance in zip(feature_names, importances):
            print(f"{name}: {importance:.3f}")