// Toast Helper Function
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast-item';
  
  let icon = 'fa-circle-info';
  if (type === 'success') icon = 'fa-circle-check';
  if (type === 'error') icon = 'fa-circle-exclamation';

  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 200);
  }, 3500);
}

// Password Show/Hide Toggle
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('toggle-password');
  const passwordInput = document.getElementById('login-password');
  const icon = document.getElementById('password-icon');

  if (toggleBtn && passwordInput && icon) {
    toggleBtn.addEventListener('click', () => {
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.className = 'fa-regular fa-eye-slash';
      } else {
        passwordInput.type = 'password';
        icon.className = 'fa-regular fa-eye';
      }
    });
  }

  // Signup Password Toggle
  const signupToggle = document.getElementById('toggle-signup-password');
  const signupPassword = document.getElementById('signup-password');
  const signupIcon = document.getElementById('signup-pwd-icon');

  if (signupToggle && signupPassword && signupIcon) {
    signupToggle.addEventListener('click', () => {
      if (signupPassword.type === 'password') {
        signupPassword.type = 'text';
        signupIcon.className = 'fa-regular fa-eye-slash';
      } else {
        signupPassword.type = 'password';
        signupIcon.className = 'fa-regular fa-eye';
      }
    });
  }

  // Login Form Submission
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      const remember = document.getElementById('remember-me') ? document.getElementById('remember-me').checked : false;

      const submitBtn = document.getElementById('login-btn');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Authenticating...';

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, remember })
        });
        const data = await response.json();

        if (data.success) {
          showToast('Login successful! Redirecting to Dashboard...', 'success');
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 600);
        } else {
          showToast(data.message || 'Login failed', 'error');
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Sign In to Dashboard';
        }
      } catch (err) {
        showToast('Network error during login. Check connection.', 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Sign In to Dashboard';
      }
    });
  }

  // Quick Demo Login Button
  const demoBtn = document.getElementById('demo-login-btn');
  if (demoBtn) {
    demoBtn.addEventListener('click', async () => {
      document.getElementById('login-email').value = 'demo@pennypal.ai';
      document.getElementById('login-password').value = 'Demo@123';
      
      const loginForm = document.getElementById('login-form');
      if (loginForm) {
        loginForm.requestSubmit();
      }
    });
  }

  // Signup Form Submission
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('signup-name').value.trim();
      const email = document.getElementById('signup-email').value.trim();
      const password = document.getElementById('signup-password').value;
      const confirm_password = document.getElementById('signup-confirm-password').value;

      if (password !== confirm_password) {
        showToast('Passwords do not match.', 'error');
        return;
      }

      const submitBtn = document.getElementById('signup-btn');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Creating Account...';

      try {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password, confirm_password })
        });
        const data = await response.json();

        if (data.success) {
          showToast('Account created successfully! Redirecting...', 'success');
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 600);
        } else {
          showToast(data.message || 'Signup failed', 'error');
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Create Account';
        }
      } catch (err) {
        showToast('Network error during signup.', 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Create Account';
      }
    });
  }
});
