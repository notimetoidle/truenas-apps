#!/bin/bash
set -euxo pipefail

# i hated doing this

workdir="$1"

while IFS= read -r values_path; do
    questions_path="${values_path/ix_values.yaml/questions.yaml}"
    test -f "$values_path"
    test -f "$questions_path"
    if grep -q "Labels Configuration (Generated)" "$questions_path"; then
        continue
    fi
    mapfile -t container_names < <(grep -A 999 "consts:" "$values_path" | grep "_container_name:" | cut -d : -f 2- | tr -d " ")
    groups_line_number=$(grep -n "groups:" "$questions_path" | cut -d : -f 1)
    head -n "$groups_line_number" "$questions_path" | tee -a "$questions_path.new"
    cat <<EOF | tee -a "$questions_path.new"
  - name: Labels Configuration (Generated)
    description: Configure Labels for Plex
EOF
    tail -n +"$(( groups_line_number + 1 ))" "$questions_path" | tee -a "$questions_path.new"
    questions_line_number=$(grep -n "questions:" "$questions_path.new" | cut -d : -f 1)
    head -n "$questions_line_number" "$questions_path.new" | tee -a "$questions_path.new2"
    cat <<EOF | tee -a "$questions_path.new2"
  - variable: labels
    label: ""
    group: Labels Configuration (Generated)
    schema:
      type: list
      default: []
      items:
        - variable: label
          label: Label
          schema:
            type: dict
            attrs:
              - variable: key
                label: Key
                schema:
                  type: string
                  required: true
              - variable: value
                label: Value
                schema:
                  type: string
                  required: true
              - variable: containers
                label: Containers
                description: Containers where the label should be applied
                schema:
                  type: list
                  items:
                    - variable: container
                      label: Container
                      schema:
                        type: string
                        required: true
                        enum:
EOF
    for container_name in "${container_names[@]}"; do
        cat <<EOF | tee -a "$questions_path.new2"
                          - value: $container_name
                            description: $container_name
EOF
    done
    echo | tee -a "$questions_path.new2"
    tail -n +"$(( questions_line_number + 1 ))" "$questions_path.new" | tee -a "$questions_path.new2"
    rm -f "$questions_path.new"
    mv "$questions_path.new2" "$questions_path"
done < <(find "$workdir" -name "ix_values.yaml")
