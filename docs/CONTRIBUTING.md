# Contributing to Adelaide Metro Tracker

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/adelaide-metro-tracking.git
   ```
3. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Code Style

- Python: Follow PEP 8
- JavaScript: Use ES6+ features
- CSS: Use CSS variables for theming
- Indentation: 4 spaces (Python), 2 spaces (JS/CSS)

## 🧪 Testing

Run tests before submitting:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Browser and version**
2. **Operating system**
3. **Steps to reproduce**
4. **Expected vs actual behavior**
5. **Screenshots** (if applicable)
6. **Console errors** (if any)

## 💡 Feature Requests

We welcome feature ideas! Please:

1. Check existing issues first
2. Describe the use case
3. Explain why it would be valuable
4. Optional: Mockups or wireframes

## 🔧 Areas for Contribution

### High Priority
- [ ] Better route matching algorithm
- [ ] Offline support / service worker
- [ ] Accessibility improvements (WCAG 2.1 AA compliance)
- [ ] More comprehensive test coverage (unit + integration tests)
- [ ] Real-time crowding indicators
- [ ] Service disruption alerts
- [ ] VoiceOver / screen reader support

### Medium Priority  
- [ ] Trip cost calculator (fare estimator)
- [ ] Weather integration (show weather at stops)
- [ ] Multiple language support (i18n)
- [ ] Favorite/saved trips
- [ ] Trip history with stats
- [ ] Export trip data (PDF/ICS)
- [ ] Real-time seat availability

### Nice to Have
- [ ] Dark/light mode toggle improvements (auto sunrise/sunset)
- [ ] Custom alert sounds (choose notification tone)
- [ ] Trip sharing via QR code
- [ ] Apple Watch / Wear OS app
- [ ] Widget support (iOS 16/Android)
- [ ] Siri/Google Assistant integration
- [ ] Augmented reality stop finder

## 🔄 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md**
5. **Submit PR** with clear description

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No console errors
- [ ] Mobile responsive

## 🏷️ Commit Messages

Use conventional commits:

```
feat: Add push notification support
fix: Correct vehicle distance calculation
docs: Update API documentation
style: Fix CSS formatting
refactor: Simplify route matching
test: Add unit tests for trip planner
chore: Update dependencies
```

## 📞 Questions?

- Open an issue for questions
- Join our Discord (if available)
- Email: me@raya.li

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Every contribution, no matter how small, helps make Adelaide Metro Tracker better for everyone.
