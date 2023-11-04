import React, {useEffect, useState} from 'react'
import ReactDOM from 'react-dom/client'
import {createBrowserRouter, RouterProvider,} from "react-router-dom"
import axios from "axios"

function getBaseUrl(): string {
    if (process.env.NODE_ENV !== 'production') return 'http://0.0.0.0:8000/api'
  return `${window.location.href}api`
}

interface ItemRequest {
    title: string,
    description: string
}

interface Item extends ItemRequest {
    id: string,
}

function HelloWorld() {
    const [item, setItem] = useState<Item>()
    const [items, setItems] = useState<Item[]>([])
    const [title, setTitle] = useState("")
    const [description, setDescription] = useState("")
    const baseUrl = getBaseUrl()
    const [triggerFetch, setTriggerFetch] = useState(0)

    function createItem() {
        const data: ItemRequest = {
            title: title,
            description: description,
        }
        axios.post(`${baseUrl}/items`, data, {
            headers: { 'Content-Type': 'application/json' },
        })
            .then(resp => {
                setItem(resp.data)
            })
            .catch(err => console.log(err))
    }

    function deleteItem(id: string) {
        axios.delete(`${baseUrl}/items/${id}`)
            .then(() => {
                setTriggerFetch(triggerFetch + 1)
            })
            .catch(err => console.log(err))
    }

    useEffect(() => {
        axios.get(`${baseUrl}/items`)
            .then((resp) => {
                setItems([...resp.data])
            })
            .catch(err => console.log(err))
    }, [baseUrl, item, triggerFetch])

    const ItemsList = items.map((item) => (
        <div>
            <h4>Title: {item.title}</h4>
            <p>Description: {item.description}</p>
            <button onClick={() => deleteItem(item.id)}>Delete Me</button>
        </div>
    ))

    return (
        <div>
          <h1>Hello world!</h1>
          <h2><a href="/other-page">Go to other page</a></h2>
            <div style={{ paddingBottom: 20}}>
                <label>
                    Add Item Title:
                    <input onChange={(e) => setTitle(e.target.value)}/>
                </label>
            </div>
            <div style={{ paddingBottom: 20}}>
                <label>
                    Add Item Description:
                    <input name="query" onChange={(e) => setDescription(e.target.value ?? "")}/>
                </label>
            </div>
            <button onClick={() => createItem()}>
                Hi, press me to hit the api
            </button>
            {item && (
                <div style={{ paddingBottom: 20}}>
                    <h2>Hi, I am data from the API</h2>
                    <h3>Item ID: {item.id}</h3>
                    <h3>Item Title: {item.title}</h3>
                    <h3>Item Description: {item.description}</h3>
                </div>
            )}
            {ItemsList}
        </div>
    )
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <HelloWorld />
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
