document.addEventListener('DOMContentLoaded', () => {
  const slides = document.querySelectorAll('.slide');
  const navItems = document.querySelectorAll('.nav-item');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const progressFill = document.querySelector('.progress-fill');
  const progressText = document.querySelector('.progress-text');
  
  let currentSlide = 0;

  // Initialize progress display on load
  progressText.textContent = `Slide 1 of ${slides.length}`;
  prevBtn.disabled = true;
  nextBtn.disabled = slides.length <= 1;
  
  // 1. Syntax Highlighting Setup
  function highlightSnippet(codeElement, lang) {
    let text = codeElement.textContent;
    
    // HTML Escape
    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
      
    if (lang === 'python' || lang === 'py') {
      // Comments: #...
      escaped = escaped.replace(/(#[^\n]*)/g, '<span class="token comment">$1</span>');
      // Double quotes strings: "..."
      escaped = escaped.replace(/(&quot;[^\n]*?&quot;)/g, '<span class="token string">$1</span>');
      // Single quotes strings: '...'
      escaped = escaped.replace(/(&#39;[^\n]*?&#39;)/g, '<span class="token string">$1</span>');
      // Numbers
      escaped = escaped.replace(/\b(\d+)\b/g, '<span class="token number">$1</span>');
      // Keywords
      const keywords = ['import', 'from', 'as', 'def', 'class', 'return', 'if', 'else', 'for', 'in', 'try', 'except', 'lambda', 'with', 'print', 'and', 'or', 'not', 'True', 'False', 'None', 'elif'];
      keywords.forEach(kw => {
        const regex = new RegExp('\\b(' + kw + ')\\b', 'g');
        escaped = escaped.replace(regex, '<span class="token keyword">$1</span>');
      });
      // Decorators
      escaped = escaped.replace(/(@[a-zA-Z_][a-zA-Z0-9_]*)/g, '<span class="token decorator">$1</span>');
      // Functions
      escaped = escaped.replace(/\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()/g, '<span class="token function">$1</span>');
    } else if (lang === 'yaml' || lang === 'yml') {
      // Comments: #...
      escaped = escaped.replace(/(#[^\n]*)/g, '<span class="token comment">$1</span>');
      // Keys: key:
      escaped = escaped.replace(/\b([a-zA-Z0-9_-]+)(?=\s*:)/g, '<span class="token keyword">$1</span>');
      // Strings/values
      escaped = escaped.replace(/(:\s+)([^\n]+)/g, '$1<span class="token string">$2</span>');
    } else if (lang === 'jinja' || lang === 'jinja2') {
      // Jinja expressions: {{ ... }}
      escaped = escaped.replace(/(\{\{[^\n]*?\}\})/g, '<span class="token decorator">$1</span>');
      // Comments
      escaped = escaped.replace(/(#[^\n]*)/g, '<span class="token comment">$1</span>');
      // Keys
      escaped = escaped.replace(/\b([a-zA-Z0-9_-]+)(?=\s*:)/g, '<span class="token keyword">$1</span>');
    } else if (lang === 'bash' || lang === 'sh') {
      // Comments
      escaped = escaped.replace(/(#[^\n]*)/g, '<span class="token comment">$1</span>');
      // Commands starts with $
      escaped = escaped.replace(/(^\$\s+)([^\n]*)/gm, '$1<span class="token function">$2</span>');
      // Strings
      escaped = escaped.replace(/(&quot;[^\n]*?&quot;)/g, '<span class="token string">$1</span>');
    }
    
    codeElement.innerHTML = escaped;
  }
  
  // Highlight all code blocks
  document.querySelectorAll('code[class^="highlight-"]').forEach(el => {
    const lang = el.className.replace('highlight-', '');
    highlightSnippet(el, lang);
  });
  
  // 2. Navigation Logic
  function goToSlide(index, direction) {
    if (index < 0 || index >= slides.length) return;
    
    const updateDOM = () => {
      slides[currentSlide].classList.remove('active');
      navItems[currentSlide].classList.remove('active');
      
      currentSlide = index;
      
      slides[currentSlide].classList.add('active');
      navItems[currentSlide].classList.add('active');
      
      // Update progress bar
      progressFill.style.width = `${(currentSlide / (slides.length - 1)) * 100}%`;
      progressText.textContent = `Slide ${currentSlide + 1} of ${slides.length}`;
      
      // Update buttons
      prevBtn.disabled = currentSlide === 0;
      nextBtn.disabled = currentSlide === slides.length - 1;
      
      // Scroll active sidebar item into view
      navItems[currentSlide].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };
    
    // Feature detect view transitions and direction
    if (document.startViewTransition && direction) {
      document.startViewTransition({
        update: updateDOM,
        types: [direction]
      });
    } else {
      updateDOM();
    }
  }
  
  function nextSlide() {
    if (currentSlide < slides.length - 1) {
      goToSlide(currentSlide + 1, 'forward');
    }
  }
  
  function prevSlide() {
    if (currentSlide > 0) {
      goToSlide(currentSlide - 1, 'backward');
    }
  }
  
  // 3. Event Listeners
  
  // Buttons
  prevBtn.addEventListener('click', prevSlide);
  nextBtn.addEventListener('click', nextSlide);
  
  // Sidebar items
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      const targetIndex = parseInt(e.currentTarget.getAttribute('data-slide-index'), 10);
      const direction = targetIndex > currentSlide ? 'forward' : 'backward';
      goToSlide(targetIndex, direction);
    });
  });
  
  // Keyboard Shortcuts
  document.addEventListener('keydown', (e) => {
    switch (e.key) {
      case 'ArrowRight':
      case ' ':
        nextSlide();
        break;
      case 'ArrowLeft':
        prevSlide();
        break;
      case 'PageDown':
        nextSlide();
        break;
      case 'PageUp':
        prevSlide();
        break;
      case 'Home':
        goToSlide(0, 'backward');
        break;
      case 'End':
        goToSlide(slides.length - 1, 'forward');
        break;
    }
  });
  
  // Touch Swipes (Mobile Support)
  let touchStartX = 0;
  let touchEndX = 0;
  
  document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, false);
  
  document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, false);
  
  function handleSwipe() {
    // Touch swipe threshold (in pixels) — extracted from CSS --swipe-threshold variable
    const swipeThreshold = 50;
    if (touchEndX < touchStartX - swipeThreshold) {
      nextSlide(); // Swiped left -> show next
    }
    if (touchEndX > touchStartX + swipeThreshold) {
      prevSlide(); // Swiped right -> show previous
    }
  }
  
  // Initialize presentation state
  goToSlide(0);
});
