# Project Style Guide

## 1. CSS Framework

- This project uses **Tailwind CSS** for all styling
- Utility classes are preferred for layout, spacing, color, and typography

## 2. Component Patterns

- All UI primitives (Button, Input, Table, Card, etc.) are implemented as React components in `frontend/shared-lib/src/components/ui/`
- Components accept a `className` prop for further customization
- Use Tailwind utility classes for all customizations

## 3. Layout & Spacing

- Use `container`, `mx-auto`, `p-4`, `space-y-*`, and `gap-*` for layout and spacing
- Use `grid` and `flex` utilities for responsive layouts

## 4. Typography

- Use Tailwind classes for font size, weight, and color (e.g., `text-xl`, `font-bold`, `text-gray-700`)

## 5. Colors & Theme

- Use the default Tailwind color palette unless otherwise specified in `tailwind.config.js`
- Reference the config for any custom colors

## 6. Forms & Inputs

- Use the `Input`, `Form`, `FormLabel`, etc. components from `shared-lib`
- Example:
  ```jsx
  <FormLabel htmlFor="email">Email</FormLabel>
  <Input id="email" type="email" />
  ```

## 7. Tables

- Use the `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableHead`, and `TableCell` components from `shared-lib`
- Example:
  ```jsx
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Name</TableHead>
        <TableHead>Email</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell>John Doe</TableCell>
        <TableCell>john@example.com</TableCell>
      </TableRow>
    </TableBody>
  </Table>
  ```

## 8. Buttons

- Use the `Button` component from `shared-lib`
- Use Tailwind classes for color and variant (e.g., `bg-blue-500`, `hover:bg-blue-600`)

## 9. Storybook

- All components should have a Storybook story for visual documentation and usage examples
- Use Storybook Docs for prop tables and usage notes

## 10. Tailwind Config Reference

- For the full color palette, spacing, and breakpoints, see `frontend/tailwind.config.js`

---

## 11. More in depth analysis asked to GitHub Copilot (raw copy&paste)

Can you summarise for me the Tailwind classes and patterns already present in the project?

GitHub Copilot
Certainly! Here’s a summary of the Tailwind CSS classes and patterns already present in your project, based on your codebase and previous context:

1. Layout & Spacing
   Containers:
   container, mx-auto, p-4, space-y-6, mb-4, gap-6
   Grid & Flex:
   grid, grid-cols-1, sm:grid-cols-2, lg:grid-cols-3, flex, items-center, justify-between, gap-4

2. Typography
   Font size & weight:
   text-3xl, text-xl, font-bold, font-semibold
   Text color:
   text-gray-700, text-gray-900, text-blue-600, text-white

3. Backgrounds & Borders
   Background color:
   bg-white, bg-blue-500, bg-blue-600, bg-gray-100
   Borders & radius:
   border, border-gray-200, rounded, rounded-lg, shadow, shadow-md

4. Buttons & Interactivity
   Button styles:
   bg-blue-500, hover:bg-blue-600, text-white, py-2, px-4, rounded, transition-colors, focus:outline-none
   Disabled/active states:
   opacity-50, cursor-not-allowed

5. Forms & Inputs
   Inputs:
   border, border-gray-300, rounded, px-3, py-2, focus:outline-none, focus:ring-2, focus:ring-blue-500
   Labels:
   block, mb-1, font-medium, text-sm

6. Tables
   Table layout:
   min-w-full, divide-y, divide-gray-200, text-left, px-6, py-4

7. Cards & Badges
   Cards:
   bg-white, shadow-md, rounded-lg, p-4
   Badges:
   inline-block, px-2, py-1, rounded-full, bg-green-100, text-green-800, text-xs

8. Miscellaneous
   Transitions & Animations:
   transition, transition-colors, duration-200
   Overflow & Scroll:
   overflow-x-auto, scrollbar-thin, scrollbar-thumb-gray-300

Patterns:
Consistent use of utility classes for spacing, color, and layout.
Responsive design with Tailwind’s breakpoint prefixes (sm:, md:, lg:).
Component props often accept className for further customization.
Minimal or no custom CSS—almost all styling is via Tailwind classes.

Summary:
Your project uses a modern, utility-first Tailwind approach for all UI, focusing on spacing, color, layout, and responsive design, with consistent patterns across components.

##

**Keep this guide up to date as you add new components or patterns**
