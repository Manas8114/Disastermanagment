import csv

def extract_links_from_csv(csv_filename):
    """
    Extracts and prints all the links from the specified CSV file.
    """
    links = []  # Use a consistent variable name

    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Assuming the 'Link' column contains the URLs
                if 'Link' in row:
                    links.append(row['Link'])
                else:
                    print("No 'Link' column found in the CSV file.")
                    break

    except FileNotFoundError:
        print(f"File {csv_filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return links

def main():
    csv_filename = r"C:\\Users\\msgok\\OneDrive\\Desktop\\disaster_news (1).csv"  # Fixed path

    links = extract_links_from_csv(csv_filename)
    
    if links:
        print("Extracted Links:")
        for link in links:  # Use a consistent variable name
            print(link)
    else:
        print("No links found.")

if __name__ == "__main__":
    main()
