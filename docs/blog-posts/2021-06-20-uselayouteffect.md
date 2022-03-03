---
tags:
  - Programming
---
# The useLayoutEffect hook

Suppose you have a parent component `A` and a child `B`, and you want to run a `useEffect` hook on mount in the parent first, followed by another `useEffect` hook in the child.

For example, you have a child component which overrides the default styles of the parent on mount.

This was a problem I faced.

You might try this, but it does not work as expected:

```javascript
const A = () => {
    useEffect(() => console.log('Parent useEffect'), [])
    console.log('Parent body')
    
    return <B/>
};

// omitted

const B = () => {
    useEffect(() => console.log('Child useEffect'), [])
    console.log('Child body')
}

/*Logs
* Parent body
* Child body
* Child useEffect
* Parent useEffect*/
```

The child component's `useEffect` is being called **before** the parent component. Why is this happening?

[`useEffect` runs after every completed render](https://reactjs.org/docs/hooks-reference.html#useeffect). If no dependencies are specified in the dependency array (the second argument), it will run after the first render.

In the above example, the parent `A` begins rendering first, followed by the child `B`. The child finishes rendering before the parent, and so its `useEffect` hook is called first, followed by the parent's.

Is there a way to run effects in the parent, before the child?

## useLayoutEffect

You can use [`useLayoutEffect`](https://reactjs.org/docs/hooks-reference.html#uselayouteffect).

`useLayoutEffect` runs synchronously, before the browser has had a chance to paint.

We can rewrite our example above to the following:

```javascript hl_lines="2"
const A = () => {
    useLayoutEffect(() => console.log('Parent useEffect'), [])
    console.log('Parent body')
    
    return <B/>
};

// omitted

const B = () => {
    useEffect(() => console.log('Child useEffect'), [])
    console.log('Child body')
}

/*Logs
* Parent body
* Child body
* Parent useEffect
* Child useEffect*/
```

Now, effects in the child run **before** the parent!

A caveat: `useLayoutEffect` is synchronous and will block visual updates, so avoid doing heavy lifting here.

The next time you need to run an effect in the parent *before* the child, consider using `useLayoutEffect`.