skills_dir := env("HOME") / ".claude" / "skills"

skills := "ddd-extract-prd ddd-model ddd-implement ddd-prd ddd-list ddd-eval"

# Install all skills as user-level symlinks
install:
    mkdir -p {{ skills_dir }}
    @for skill in {{ skills }}; do \
        ln -sf "$(pwd)/skills/$skill" "{{ skills_dir }}/$skill"; \
        echo "linked $skill"; \
    done

# Lint skills against Anthropic best practices
lint:
    python3 qa/lint_skills.py

# Run QA tests
test:
    cd qa && python3 -m pytest -v

# Remove all skill symlinks
uninstall:
    @for skill in {{ skills }}; do \
        rm -f "{{ skills_dir }}/$skill"; \
        echo "removed $skill"; \
    done
