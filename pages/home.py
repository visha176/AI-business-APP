import streamlit as st

def show_home():
    st.markdown("""
        <style>
        /* Ensure the full-page container takes the entire viewport */
        .full-page {
            height: 110vh;
            width: 100vw;
            margin: 0;
            padding: 0;
            
        }
        @media (min-width: calc(736px + 8rem)) {
    .st-emotion-cache-zy6yx3 {
        padding-left: 0rem;
        padding-right: 0rem;
    }
}

        /* Top half with a full-width background image */
        .top-half {
            width: 100%;
            height: 80%;
            background-image: url('https://i.im.ge/2024/08/25/fNtnVq.Welcome-to-1.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            margin-top: -4.2rem;
        }

        /* Bottom half centered */
        .bottom-half {
            width: 100%;
            height: auto;
            background-color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 2rem 0;
        }

        /* Card styles */
        .card-container {
            display: flex;
            justify-content: space-around;
            width: 100%;
            margin-top: 2rem;
        }

        .card {
            background-color: #f8f9fa;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 22%;
            height: 300px;  /* Increased card height */
            text-align: center;
            font-family: "Source Sans Pro", sans-serif;
            font-weight: 600;
            color: rgb(49, 51, 63);
        }

        .card h2 {
            margin-bottom: 1rem;
            font-size: 24px;
        }

        .card p {
            font-size: 16px;
            line-height: 1.5;
        }

        /* Flex layout for left and right sections */
        .section-container {
            display: flex;
            justify-content: space-between;
            width: 100%;
            padding: 2rem;
            margin-top: -40rem;
        }

        /* Style for left and right sections containers */
        .left-sections, .right-sections {
            display: flex;
            flex-direction: column;
            width: 48%; /* Adjust width to fit within the container */
        }

        /* Ensure left sections are aligned to the left */
        .left-sections {
            align-items: flex-start;
            width: 20%;
            margin-top: 12rem;
            margin-left: 10rem;
        }

        /* Ensure right sections are aligned to the right */
        .right-sections {
            align-items: flex-end;
            display: flex;
            flex-direction: column;
            width: 20%;
            margin-top: 12rem;
            margin-right: 10rem;
        }

        /* Individual section style */
        .section {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            margin-top: 2rem;
        }

        /* Icon styles */
        .section img {
            width: 50px; /* Adjust icon size */
            height: 50px; /* Adjust icon size */
            margin-right: 1rem; /* Space between icon and text */
        }

        /* Image container styles */
        .image-container {
            display: flex;
            justify-content: center;
            width: 100%;
            margin-top: 2rem;
            gap: 2rem;
        }

        .image-container img {
            width: 20%;
            height: 300px;  /* Set a fixed height for the images */
            object-fit: cover;  /* Maintain aspect ratio and cover the area */
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }

        /* Image between sections */
        .image-between-sections {
            display: flex;
            justify-content: center;
            width: 30%;
            margin: 2rem 0;
            margin-top: 5rem;
        }

        .image-between-sections img {
            max-width: 60%; /* Adjust width as needed */
            height: auto;
            object-fit: cover;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
        /* New section for statistics */
        .stats-container {
            display: flex;
            justify-content: space-around;
            background-image: url('https://emc2rrspvpp.exactdn.com/wp-content/themes/centricSoftware/img/correct-glow.jpg');
            padding: 50px 0;
            margin-top: 3rem;
            width: 100%;
            height: 30%;
            
        }

        .stat-item {
            text-align: center;
            color: #ffffff;
            width: 30%;
        }

        .stat-item h3 {
            font-size: 48px;
            margin-bottom: 10px;
            color: white;
            margin-left: 2rem;
        }

        .stat-item p {
            font-size: 24px;
            margin-bottom: 5px;
            color: #0b7fe4;
        }

        .stat-item span {
            font-size: 16px;
            color: #a3a3a3;
        }
        
     /* Header styles */
        .header {
            background-color: #007bff;
            color: white;
            padding: 2rem;
            text-align: center;
        }

        .header h1 {
            font-size: 36px;
            margin: 0;
        }

        /* Footer styles */
        .footer {
        background-color: #010407;
        padding: 2rem 1rem;
        border-top: 1px solid #ffffff;
        
        width: 100vw;
        margin-bottom: -3rem;
        }

        .footer-content {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }

        .footer-content > div {
            flex: 1;
            margin: 1rem;
        }

        .footer-logo img {
        max-width: 200px;
        height: 60px;
        }

        .footer-content h4 {
            margin: 1rem 0;
            font-size: 18px;
            color: white;
        }

        .footer-content p {
            font-size: 14px;
            color: white;
        }

        .footer-links {
            margin-bottom: 1rem;
        }

        .footer-links a {
            text-decoration: none;
            color: #007bff;
            font-size: 14px;
        }

        .footer-links a:hover {
            text-decoration: underline;
        }

        .footer-contact p {
            font-size: 14px;
            color: white;
        }

        .footer-newsletter input[type="email"] {
            padding: 0.5rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
            margin-right: 0.5rem;
        }

        .footer-newsletter button {
            padding: 0.5rem 1rem;
            border: none;
            background-color: #007bff;
            color: white;
            border-radius: 4px;
            cursor: pointer;
        }

        .footer-newsletter button:hover {
            background-color: #0056b3;
        }
               .get-started {
                font-size: 1.5em;
                color: #555;
                margin-bottom: 20px;
            }
           .header {
            background-color: white;
            color: white;
            text-align: center;
            padding: 2rem;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 0.5rem;
        }
        
        .header h2 {
            font-size: 18px;
            margin-bottom: 1rem;
        }
        
        .header h3 {
            margin-bottom: 1rem;
        }
        
        .contact-button {
            background-color: #007bff;
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 16px;
        }
        
        .contact-button:hover {
            background-color: #0056b3;
        } 
                .st-emotion-cache-asc41u a {
        color: rgb(250 253 255);
        background-color: #106fc0;
    }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="full-page">
        <div class="top-half"></div>
        <div class="bottom-half">
            <!-- Content for the bottom half of the page -->
            <h1>Our Services</h1>
            <div class="card-container">
                <div class="card">
                    <h2>Internal Store Transfers</h2>
                    <p>Optimize internal transfers to ensure timely and efficient movement of stock between stores, improving availability and reducing overstock.</p>
                </div>
                <div class="card">
                    <h2>Assortment Planning</h2>
                    <p>Develop and execute strategic assortment plans to meet consumer demand, enhance product mix, and maximize sales opportunities.</p>
                </div>
                <div class="card">
                    <h2>Replenishment Management</h2>
                    <p>Automate replenishment processes to maintain optimal inventory levels, reduce stockouts, and ensure product availability across all locations.</p>
                </div>
                <div class="card">
                    <h2>Inventory Optimization</h2>
                    <p>Implement advanced inventory management techniques to balance stock levels, minimize holding costs, and increase overall efficiency.</p>
                </div>
            </div>
            <!-- Image between sections -->
            <div class="image-between-sections">
                <img src="https://zrtechsolutions.com/demo/html/technoit/assets/images/features.jpg" alt="Image Between Sections">
            </div>
            <!-- Sections with icons and text -->
            <div class="section-container">
                <div class="left-sections">
                    <div class="section">
                        <div>
                            <h2>Pricing</h2>
                            <p>Choose a plan that fits your needs, and get started today.</p>
                        </div>
                    </div>
                    <div class="section">
                        <div>
                            <h2>Features</h2>
                            <p>Explore a wide range of features designed to enhance your experience.</p>
                        </div>
                    </div>
                </div>
                <div class="right-sections">
                    <div class="section">
                        <div>
                            <h2>Support</h2>
                            <p>We're here to provide you with the best support whenever you need it.</p>
                        </div>
                    </div>
                    <div class="section">
                        <div>
                            <h2>Contact</h2>
                            <p>Reach out to us anytime for assistance, and our team will be happy to help you.</p>
                        </div>
                    </div>
                </div>
            </div>
                <div class="stats-container">
        <div class="stat-item">
            <img src="https://zrtechsolutions.com/demo/html/technoit/assets/images/icons/complete-projects.svg" alt="Projects Icon" width="50" height="50">
            <h3>10,000</h3>
            <p>Projects</p>
        </div>
        <div class="stat-item">
            <img src="https://zrtechsolutions.com/demo/html/technoit/assets/images/icons/happy-clients.svg" alt="Clients Icon" width="50" height="50">
            <h3>500</h3>
            <p>Clients</p>
        </div>
        <div class="stat-item">
            <img src="https://zrtechsolutions.com/demo/html/technoit/assets/images/icons/hours-support.svg" alt="Satisfaction Icon" width="50" height="50">
            <h3>99%</h3>
            <p>Satisfaction</p>
        </div>
    </div>
            <!-- Re-added image section -->
            <div class="image-container">
                <img src="https://emc2rrspvpp.exactdn.com/wp-content/uploads/2022/02/Resource-1.jpg?lossy=1&quality=92&webp=92&ssl=1" alt="Image 1">
                <img src="https://emc2rrspvpp.exactdn.com/wp-content/uploads/2022/03/Resource-2.jpg?lossy=1&quality=92&webp=92&ssl=1" alt="Image 2">
                <img src="https://emc2rrspvpp.exactdn.com/wp-content/uploads/2024/01/2023-CMI-in-review.jpg?lossy=1&quality=92&webp=92&ssl=1" alt="Image 3">
            </div>
            <!-- Re-added image section -->
            <div class="image-container">
                <img src="https://emc2rrspvpp.exactdn.com/wp-content/uploads/2023/07/Swarovski-hero-scaled.jpg?lossy=1&quality=92&webp=92&ssl=1" alt="Image 1">
                <img src="https://emc2rrspvpp.exactdn.com/wp-content/uploads/2023/10/Neiman-Marcus-hero-scaled.jpg?lossy=1&quality=92&webp=92&ssl=1" alt="Image 2">
                <img src="https://emc2rrspvpp.exactdn.com/wp-content/uploads/2022/09/Rothys-1.jpg?lossy=1&quality=92&webp=92&ssl=1" alt="Image 3">
            </div>
  <div>     
<div class="header">
<h1>Get Started</h1>
<h2>Let’s Make Something Great Together</h2>
<h3><a href="#contact" class="contact-button">Contact Us</a></h3>
</div>
                </div>
 <div class="footer">
        <div class="footer-content">
            <div class="footer-logo">
                 <img src="https://i.im.ge/2024/08/25/fNwfzK.WhatsApp-Image-2024-08-22-at-4-08-55-PM-removebg-preview.png" alt="Image Between Sections">
            </div>
            <div class="footer-links">
    <h4>Services</h4>
    <a href="#">Internal Store Transfers</a><br>
    <a href="#">Assortment Planning</a><br>
    <a href="#">Replenishment Management</a>
    
</div>
            <div class="footer-links">
                <h4>Information</h4>
                <a href="#">About</a><br>
                <a href="#">Pricing</a><br>
                <a href="#">Team</a><br>
                <a href="#">Portfolio</a><br>
                <a href="#">FAQs</a><br>
                <a href="#">Blogs</a><br>
                <a href="#">Blog Details</a><br>
                <a href="#">Coming Soon</a><br>
                <a href="#">Terms & Conditions</a><br>
                <a href="#">Privacy Policy</a>
            </div>
            <div class="footer-contact">
                <h4>Contact Us</h4>
                <p></p>
                <p></p>
                <p>contact@example.com</p>
            </div>
            <div class="footer-newsletter">
                <h4>Newsletter</h4>
                <p>Don't miss to subscribe to our new feeds, kindly fill the form below.</p>
                <form action="#">
                    <input type="email" placeholder="Your email">
                    <button type="submit">Subscribe</button>
                </form>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
