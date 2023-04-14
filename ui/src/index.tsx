import React from 'react'
import ReactDOM from 'react-dom/client'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom"

const router = createBrowserRouter([
  {
    path: "/",
    element:
        <div>
          <h1>Hello world!</h1>
          <h2><a href="/other-page">Go to other page</a></h2>
        </div>,
  },
  {
    path: "/other-page",
    element:
        <div>
            <h1>Goodbye, my friend!</h1>
            <h2><a href="/">Go home</a></h2>
        </div>,
  },
])

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
)
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
