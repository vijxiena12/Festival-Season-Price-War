// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyAk5R0dWiRAyKdIqa0WnocdqkfhTptSyFk",
    authDomain: "ads-project-dfd93.firebaseapp.com",
    projectId: "ads-project-dfd93",
    storageBucket: "ads-project-dfd93.firebasestorage.app",
    messagingSenderId: "974516291458",
    appId: "1:974516291458:web:42734b8547c5c16515719b",
    measurementId: "G-LVFBBHKGNQ"
};

// Initialize Firebase
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}

// Check authentication state
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        // User is signed in
        updateAuthUI(user);
        
        // DO NOT auto-redirect from login/signup pages
        // Let users manually authenticate through the forms
        // Only redirect to login from protected pages if user is signed out
    } else {
        // User is signed out
        updateAuthUI(null);
        
        // Redirect to login only from protected pages
        if (window.location.pathname.endsWith('dashboard.html') ||
            window.location.pathname.endsWith('price-comparison.html') ||
            window.location.pathname.endsWith('trends.html') ||
            window.location.pathname.endsWith('insights.html')) {
            window.location.href = 'login.html';
        }
    }
});

// Update UI based on authentication state
function updateAuthUI(user) {
    const authElements = document.querySelectorAll('.auth-required');
    const unauthElements = document.querySelectorAll('.unauth-required');
    const userDisplay = document.getElementById('user-display');
    const signOutButton = document.getElementById('signOutBtn');
    
    if (user) {
        // User is signed in
        authElements.forEach(element => {
            element.style.display = 'block';
        });
        unauthElements.forEach(element => {
            element.style.display = 'none';
        });
        
        // Update user display
        if (userDisplay) {
            const displayName = user.displayName || 'User';
            const email = user.email || '';
            const photoURL = user.photoURL || '';
            
            userDisplay.textContent = displayName;
            
            // Update user avatar if exists
            const userAvatar = document.getElementById('user-avatar');
            if (userAvatar) {
                if (photoURL) {
                    userAvatar.src = photoURL;
                    userAvatar.alt = displayName;
                    userAvatar.classList.remove('hidden');
                    const fallback = document.getElementById('user-avatar-fallback');
                    if (fallback) fallback.classList.add('hidden');
                } else {
                    const fallback = document.getElementById('user-avatar-fallback');
                    if (fallback) {
                        fallback.textContent = displayName.charAt(0).toUpperCase();
                        fallback.classList.remove('hidden');
                    }
                    userAvatar.classList.add('hidden');
                }
            }
        }
        
        // Add sign out event listener
        if (signOutButton) {
            signOutButton.addEventListener('click', signOut);
        }
    } else {
        // User is signed out
        authElements.forEach(element => {
            element.style.display = 'none';
        });
        unauthElements.forEach(element => {
            element.style.display = 'block';
        });
    }
}

// Sign out function
function signOut() {
    firebase.auth().signOut().then(() => {
        // Sign-out successful
        window.location.href = 'index.html';
    }).catch((error) => {
        console.error('Sign out error:', error);
    });
}

// Handle sign up with email/password
function handleSignUp(email, password, displayName) {
    firebase.auth().createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // Update user profile with display name
            return userCredential.user.updateProfile({
                displayName: displayName
            });
        })
        .then(() => {
            // Redirect to dashboard after successful sign up
            window.location.href = 'dashboard.html';
        })
        .catch((error) => {
            console.error('Sign up error:', error);
            alert(error.message);
        });
}

// Handle sign in with email/password
function handleSignIn(email, password) {
    firebase.auth().signInWithEmailAndPassword(email, password)
        .then(() => {
            // Redirect to dashboard after successful sign in
            window.location.href = 'dashboard.html';
        })
        .catch((error) => {
            console.error('Sign in error:', error);
            alert(error.message);
        });
}

// Handle Google sign in
function signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithPopup(provider)
        .then(() => {
            // Redirect to dashboard after successful Google sign in
            window.location.href = 'dashboard.html';
        })
        .catch((error) => {
            console.error('Google sign in error:', error);
            alert(error.message);
        });
}

// Handle GitHub sign in
function signInWithGitHub() {
    const provider = new firebase.auth.GithubAuthProvider();
    firebase.auth().signInWithPopup(provider)
        .then(() => {
            // Redirect to dashboard after successful GitHub sign in
            window.location.href = 'dashboard.html';
        })
        .catch((error) => {
            console.error('GitHub sign in error:', error);
            alert(error.message);
        });
}

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            const expanded = mobileMenuButton.getAttribute('aria-expanded') === 'true' || false;
            mobileMenuButton.setAttribute('aria-expanded', !expanded);
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Handle sign up form submission
    const signUpForm = document.getElementById('signup-form');
    if (signUpForm) {
        signUpForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;
            const displayName = document.getElementById('signup-name').value;
            
            if (password !== document.getElementById('signup-confirm-password').value) {
                alert("Passwords don't match!");
                return;
            }
            
            handleSignUp(email, password, displayName);
        });
    }
    
    // Handle sign in form submission
    const signInForm = document.getElementById('signin-form');
    if (signInForm) {
        signInForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('signin-email').value;
            const password = document.getElementById('signin-password').value;
            
            handleSignIn(email, password);
        });
    }
    
    // Handle Google sign in button
    const googleSignInButton = document.getElementById('google-signin');
    if (googleSignInButton) {
        googleSignInButton.addEventListener('click', signInWithGoogle);
    }
    
    // Handle GitHub sign in button
    const githubSignInButton = document.getElementById('github-signin');
    if (githubSignInButton) {
        githubSignInButton.addEventListener('click', signInWithGitHub);
    }
});
