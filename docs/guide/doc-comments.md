---
title: Doc Comments
---

# Writing Fortran Doc Comments

## Where to Place Comments

```fortran
module my_module
!< Module description.            <-- after module statement

integer :: MY_CONST = 42 !< Constant description.  <-- same line as declaration

type :: my_type
   !< Type description.           <-- after type statement
   real :: x !< Component doc.    <-- same line as component
   contains
      procedure :: init !< Bound procedure doc.
endtype

contains

subroutine do_work(self, n)
!< Subroutine description.        <-- after subroutine statement
!< Can span multiple lines.
!< Supports **Markdown** and $\LaTeX$.
class(my_type), intent(inout) :: self !< The object.
integer,        intent(in)    :: n    !< Iteration count.
```

## Doc Comment Rules

1. Use `!<` (not `!!`) when `docmark: <` is set in the FORD project file
2. Module/type/procedure docs go on lines **immediately after** the statement
3. Variable/argument docs go on the **same line** as the declaration
4. Multi-line docs: continue with `!<` on subsequent lines
5. In table cells, only the **first line** is shown (full text in block descriptions)
6. Markdown and LaTeX are fully supported in doc comments

## Tips for Good Doc Comments

- **First line matters**: for variables and type components, keep the first line short and descriptive -- it becomes the table cell content
- **Describe "what", not "how"**: `!< Conservative variables vector` not `!< A real array`
- **Units and ranges**: `!< CFL number (0 < cfl <= 1)` or `!< Temperature [K]`
- **Cross-references**: use module/type names in backticks for readability

## LaTeX Math Support

Math rendering is enabled via `markdown: { math: true }` in `config.mts` (uses `markdown-it-mathjax3`).

### In Hand-Written Markdown Pages

```markdown
Inline: $E = mc^2$

Display:
$$
\frac{\partial u}{\partial t} + \nabla \cdot \mathbf{F}(u) = 0
$$
```

### In Fortran Doc Comments

Both LaTeX delimiter styles work:

```fortran
subroutine compute_flux(q, f)
!< Compute flux using: $F = \rho u \mathbf{e}_x$
!<
!< The Euler equations in conservation form:
!< $$
!< \frac{\partial U}{\partial t} + \frac{\partial F}{\partial x} = 0
!< $$
```

Or with `\(...\)` and `\[...\]` notation:

```fortran
!< Approximate \(\frac{dq}{ds}\) at \(x_i\) as:
!< \[
!< \frac{dq}{ds}\bigg|_i \approx \frac{1}{\Delta s} \sum_{m} c_m q_{i+m}
!< \]
```

## Fortran Syntax Highlighting

VitePress highlights Fortran code blocks. Use any of these language tags:

````markdown
```fortran
program hello
  implicit none
  print *, "Hello!"
end program
```
````

Tags `fortran`, `f90`, `f95`, `f03`, `f08` all map to free-form Fortran. Use `f77` for fixed-form.
