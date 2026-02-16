skills_dir := env("HOME") / ".claude" / "skills"

skills := "ddd-extract-prd ddd-model ddd-implement ddd-prd ddd-list"

# Install all skills as user-level symlinks
install:
    mkdir -p {{ skills_dir }}
    @for skill in {{ skills }}; do \
        ln -sf "$(pwd)/skills/$skill" "{{ skills_dir }}/$skill"; \
        echo "linked $skill"; \
    done

# Remove all skill symlinks
uninstall:
    @for skill in {{ skills }}; do \
        rm -f "{{ skills_dir }}/$skill"; \
        echo "removed $skill"; \
    done
