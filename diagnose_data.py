import psycopg2
import os
from dotenv import load_dotenv

def diagnose_data():
    """
    Diagnostic script to understand why we're only getting 59 customers
    """
    
    # Load environment variables
    load_dotenv("/app/.env")
    USER = os.getenv("SUPABASE_USER")
    PASSWORD = os.getenv("SUPABASE_PASSWORD")
    HOST = os.getenv("SUPABASE_HOST")
    PORT = os.getenv("SUPABASE_PORT")
    DBNAME = os.getenv("SUPABASE_DBNAME")
    
    try:
        with psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        ) as connection:
            with connection.cursor() as cursor:
                
                print("=== DATA DIAGNOSIS ===\n")
                
                # 1. Check total customers
                cursor.execute("SELECT COUNT(*) FROM customer;")
                total_customers = cursor.fetchone()[0]
                print(f"1. Total customers in database: {total_customers}")
                
                # 2. Check total invoices
                cursor.execute("SELECT COUNT(*) FROM invoice;")
                total_invoices = cursor.fetchone()[0]
                print(f"2. Total invoices: {total_invoices}")
                
                # 3. Check total invoice lines
                cursor.execute("SELECT COUNT(*) FROM invoice_line;")
                total_invoice_lines = cursor.fetchone()[0]
                print(f"3. Total invoice lines: {total_invoice_lines}")
                
                # 4. Check total tracks
                cursor.execute("SELECT COUNT(*) FROM track;")
                total_tracks = cursor.fetchone()[0]
                print(f"4. Total tracks: {total_tracks}")
                
                # 5. Check total genres
                cursor.execute("SELECT COUNT(*) FROM genre;")
                total_genres = cursor.fetchone()[0]
                print(f"5. Total genres: {total_genres}")
                
                # 6. Check tracks with NULL genre_id
                cursor.execute("SELECT COUNT(*) FROM track WHERE genre_id IS NULL;")
                tracks_no_genre = cursor.fetchone()[0]
                print(f"6. Tracks with no genre: {tracks_no_genre}")
                
                # 7. Check customers with purchases
                cursor.execute("""
                    SELECT COUNT(DISTINCT c.customer_id) 
                    FROM customer c
                    JOIN invoice i ON c.customer_id = i.customer_id
                    JOIN invoice_line il ON i.invoice_id = il.invoice_id;
                """)
                customers_with_purchases = cursor.fetchone()[0]
                print(f"7. Customers with purchases: {customers_with_purchases}")
                
                # 8. Check customers with purchases that have genre info
                cursor.execute("""
                    SELECT COUNT(DISTINCT c.customer_id) 
                    FROM customer c
                    JOIN invoice i ON c.customer_id = i.customer_id
                    JOIN invoice_line il ON i.invoice_id = il.invoice_id
                    JOIN track t ON il.track_id = t.track_id
                    WHERE t.genre_id IS NOT NULL;
                """)
                customers_with_genre_purchases = cursor.fetchone()[0]
                print(f"8. Customers with genre-linked purchases: {customers_with_genre_purchases}")
                
                # 9. Check the full join result before filtering
                cursor.execute("""
                    SELECT COUNT(DISTINCT c.customer_id) 
                    FROM customer c
                    JOIN invoice i ON c.customer_id = i.customer_id
                    JOIN invoice_line il ON i.invoice_id = il.invoice_id
                    JOIN track t ON il.track_id = t.track_id
                    JOIN genre g ON t.genre_id = g.genre_id;
                """)
                full_join_customers = cursor.fetchone()[0]
                print(f"9. Customers after all joins: {full_join_customers}")
                
                # 10. Show some sample genre distribution
                cursor.execute("""
                    SELECT g.name, COUNT(DISTINCT c.customer_id) as customer_count
                    FROM customer c
                    JOIN invoice i ON c.customer_id = i.customer_id
                    JOIN invoice_line il ON i.invoice_id = il.invoice_id
                    JOIN track t ON il.track_id = t.track_id
                    JOIN genre g ON t.genre_id = g.genre_id
                    GROUP BY g.name
                    ORDER BY customer_count DESC
                    LIMIT 10;
                """)
                genre_distribution = cursor.fetchall()
                print(f"\n10. Top 10 genres by customer count:")
                for genre, count in genre_distribution:
                    print(f"    {genre}: {count} customers")
                
                # 11. Check if the issue is in our WHERE clause
                cursor.execute("""
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
                    )
                    SELECT COUNT(DISTINCT customer_id) FROM customer_genre_purchases;
                """)
                customers_in_cte = cursor.fetchone()[0]
                print(f"\n11. Customers in first CTE: {customers_in_cte}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_data()