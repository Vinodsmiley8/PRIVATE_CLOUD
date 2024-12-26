import os

# Function to get the folder structure from file paths and map them to links
def get_folder_structure_with_links(file_paths, links_dict):
    folder_structure = {}
    
    for path in file_paths:
        parts = path.split(os.sep)
        current = folder_structure
        
        # Build the folder structure dynamically
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add the download link from the links_dict
        if path in links_dict:
            current['link'] = links_dict[path]
    
    return folder_structure

# Function to read SERVER_PATHS_DOWNLOAD.txt file and map paths to Mega links
def read_paths_and_links(file_path):
    paths = []
    links_dict = {}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Extract file paths and Mega links
        for line in lines:
            parts = line.split(' => ')
            if len(parts) == 2:
                path = parts[0].strip()
                link = parts[1].strip()
                paths.append(path)
                links_dict[path] = link
                
    return paths, links_dict

# Function to render HTML with Bootstrap and interactive dropdowns
def render_html(folder_structure):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Private Cloud</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
    let waveCircles = [];
    function createWave(x, y) {
        const wave = document.createElement('div');
        wave.className = 'wave';
        wave.style.left = `${x - 75}px`;  // Adjust wave center based on larger size
        wave.style.top = `${y - 75}px`;   // Adjust wave center based on larger size

        // Neutral wave color (transparent background)
        wave.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';

        // Append wave to body and animate it
        document.body.appendChild(wave);
        waveCircles.push(wave);

        // Animate wave expansion with smoothness and larger size
        wave.animate(
            [
                { transform: 'scale(0)', opacity: 0.4 },
                { transform: 'scale(1)', opacity: 0 }  // Larger wave size for smoother animation
            ],
            {
                duration: 600,  // Slightly longer duration for smoother effect
                easing: 'ease-out',
                fill: 'forwards'
            }
        );

        // Clean up after animation
        setTimeout(() => {
            wave.remove();
            waveCircles = waveCircles.filter(w => w !== wave);
        }, 600);
    }

    document.addEventListener('mousemove', (e) => {
        createWave(e.clientX, e.clientY);
    });
</script>

<style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
                height: 100vh;
                overflow-y: auto;
                overflow-x: hidden;
                color: white;
            }
            canvas {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
            }
            .folder-link, .file-link {
                font-weight: bold;
                cursor: pointer;
                color: #f9d423;
                transition: transform 0.3s ease, box-shadow 0.3s ease, color 0.3s ease, font-size 0.3s ease; /* Smooth transitions */
                display: inline-block;
                font-size: 18px; /* Increased text size */
            }

            /* Hover effect to slightly increase text size and add 3D effect */
            .folder-link:hover, .file-link:hover {
                transform: perspective(600px) translateY(-5px) rotateX(10deg) rotateY(5deg); /* 3D effect */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Shadow for 3D effect */
                color: #32CD32; /* New hover color */
                font-size: 20px;  /* Slightly larger text on hover */
            }

            /* Smooth folder dropdown appearance */
            .nested {
                display: none;
                padding-left: 20px;
                transition: all 0.5s ease-in-out; /* Smooth opening and closing */
            }

            .nested.show {
                display: block;
                transition: all 0.5s ease-in-out; /* Smooth opening and closing */
            }

            .folder-link:hover + .nested, .file-link:hover + .nested {
                display: block;
            }

            .content {
                padding: 20px;
            }
            .wave {
                position: absolute;
                width: 150px;  /* Increased wave size to 150px */
                height: 150px; /* Increased wave size to 150px */
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.2);  /* Neutral wave color */
                pointer-events: none;
            }
        </style>
    </head>
    <body>
        <canvas id="background"></canvas>
        <div class="content">
            <h2 class="text-center mb-4">PRIVATE CLOUD WITH LINKS</h2>
            <ul class="list-group">
    """
    
    # Recursive function to generate folder structure HTML
    def recursive_html(folder_structure):
        html = ""
        for folder, subfolders in folder_structure.items():
            is_folder = len(subfolders) > 0
            folder_class = "folder-link" if is_folder else "file-link"
            link = subfolders.get('link', None)
            
            # Make the filename clickable if a link exists
            link_text = f'<a href="{link}" class="file-link" target="_blank">{folder}</a>' if link else folder
            
            html += f"""
            <li class="list-group-item">
                <span class="{folder_class}" onclick="toggleNested('{folder}')">{link_text}</span>
                {render_subfolders(subfolders, folder)}
            </li>
            """
        return html
    
    # Function to render nested subfolders
    def render_subfolders(subfolders, folder):
        if not subfolders or 'link' in subfolders:
            return ""
        return f'<ul id="{folder}" class="nested">{recursive_html(subfolders)}</ul>'
    
    # Generate the folder structure
    html_content += recursive_html(folder_structure)
    html_content += """
            </ul>
        </div>

        <script>
            let openFolders = new Set();

            function toggleNested(folder) {
                const element = document.getElementById(folder);
                const isVisible = element.classList.contains('show');
                
                // Toggle the visibility of subfolders
                element.classList.toggle('show');
                
                // If the folder is opened by click, add it to the openFolders set
                if (!isVisible) {
                    openFolders.add(folder);
                } else {
                    openFolders.delete(folder);
                }
            }
        </script>
    </body>
    </html>
    """
    
    return html_content

# Get the paths and Mega links from SERVER_PATHS_DOWNLOAD.txt
file_paths, links_dict = read_paths_and_links('SERVER_PATHS_DOWNLOAD.txt')  # Adjust path if necessary

# Generate the folder structure with links
folder_structure = get_folder_structure_with_links(file_paths, links_dict)

# Generate the HTML
html_output = render_html(folder_structure)

# Save the generated HTML to output.html
with open('output.html', 'w') as html_file:
    html_file.write(html_output)

# print("HTML file 'output.html' with hoverable dropdowns and modern styling generated successfully!")
