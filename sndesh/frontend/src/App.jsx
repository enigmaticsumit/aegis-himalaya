
import { useState } from 'react'
import {
  ShieldAlert,
  CloudRain,
  Newspaper,
  Package,
  MapPin,
  Upload,
  Send,
  CheckCircle,
  Activity,
  Navigation,
  X,
  Bot,
  User,
  Clock,
} from 'lucide-react'

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from 'react-leaflet'

import 'leaflet/dist/leaflet.css'
import './App.css'

const mockData = {
  disaster: 'Landslide Risk',
  severity: 'HIGH',
  temperature: '18°C',
  humidity: '76%',
  news: 'Heavy rainfall reported in the Himalayan region',
  inventory: '240 Relief Kits',
}

function MapUpdater({ position }) {
  const map = useMap()

  map.flyTo(position, 10, { duration: 1 })

  return null
}

export default function App() {
  const [location, setLocation] = useState('Jammu')
  const [latitude, setLatitude] = useState('32.7357')
  const [longitude, setLongitude] = useState('74.8697')
  const [position, setPosition] = useState([32.7357, 74.8697])

  const [image, setImage] = useState(null)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hello! I am VEKTOR. I can help you monitor disaster conditions and coordinate relief missions.',
    },
  ])

  const [approved, setApproved] = useState(false)

  function searchLocation() {
    const lat = Number(latitude)
    const lng = Number(longitude)

    if (
      location.trim() === '' ||
      !Number.isFinite(lat) ||
      !Number.isFinite(lng) ||
      lat < -90 ||
      lat > 90 ||
      lng < -180 ||
      lng > 180
    ) {
      alert('Please enter a valid location and coordinates.')
      return
    }

    setPosition([lat, lng])
  }

  function sendMessage() {
    if (!message.trim()) return

    const userMessage = message

    setMessages((previous) => [
      ...previous,
      { role: 'user', text: userMessage },
      {
        role: 'assistant',
        text: `This is a sample VEKTOR response for ${location}. Your query has been received. Live AI analysis will be connected to the backend later.`,
      },
    ])

    setMessage('')
  }

  function uploadImage(event) {
    const file = event.target.files?.[0]

    if (!file) return

    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file.')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('Image must be smaller than 10 MB.')
      return
    }

    if (image?.url) URL.revokeObjectURL(image.url)

    setImage({
      name: file.name,
      url: URL.createObjectURL(file),
    })
  }

  return (
    <div className="min-h-screen bg-[#080d18] text-white">

      {/* HEADER */}
      <header className="border-b border-slate-800 bg-[#0d1525]">
        <div className="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-cyan-400 tracking-wider">
              VEKTOR
            </h1>
            <p className="text-xs text-slate-400">
              DISASTER INTELLIGENCE SYSTEM
            </p>
          </div>

          <div className="flex items-center gap-2 text-sm text-emerald-400">
            <Activity size={17} />
            System Online
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-5 md:p-7 space-y-7">

        {/* TITLE */}
        <section>
          <p className="text-cyan-400 text-sm font-semibold">
            COMMAND CENTER / OVERVIEW
          </p>

          <h2 className="text-3xl md:text-4xl font-bold mt-2">
            Disaster Command Dashboard
          </h2>

          <p className="text-slate-400 mt-2">
            Monitor risks. Coordinate relief. Save time.
          </p>
        </section>

        {/* LOCATION SEARCH */}
        <section className="bg-[#111c30] border border-slate-800 rounded-2xl p-5">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Navigation className="text-cyan-400" size={19} />
            Location Intelligence
          </h3>

          <div className="grid md:grid-cols-4 gap-3">
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Enter location"
              className="input-field md:col-span-2"
            />

            <input
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              placeholder="Latitude"
              className="input-field"
            />

            <input
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              placeholder="Longitude"
              className="input-field"
            />
          </div>

          <button
            onClick={searchLocation}
            className="primary-button mt-4"
          >
            <MapPin size={17} />
            Update Location
          </button>
        </section>

        {/* DASHBOARD CARDS */}
        <section className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4">

          <DashboardCard
            icon={<ShieldAlert />}
            title="Disaster Status"
            value={mockData.disaster}
            detail={mockData.severity + ' RISK'}
            color="text-red-400"
          />

          <DashboardCard
            icon={<CloudRain />}
            title="Weather"
            value={mockData.temperature}
            detail={`Humidity ${mockData.humidity}`}
            color="text-cyan-400"
          />

          <DashboardCard
            icon={<Newspaper />}
            title="Latest News"
            value="Regional Alert"
            detail={mockData.news}
            color="text-amber-400"
          />

          <DashboardCard
            icon={<Package />}
            title="Relief Inventory"
            value={mockData.inventory}
            detail="Sample available stock"
            color="text-emerald-400"
          />

        </section>

        {/* MAP AND APPROVAL */}
        <section className="grid lg:grid-cols-2 gap-5">

          {/* MAP */}
          <div className="dashboard-panel">
            <h3 className="panel-title">
              <MapPin className="text-cyan-400" />
              Disaster Location Map
            </h3>

            <p className="text-sm text-slate-400 mb-4">
              Current monitoring area: {location}
            </p>

            <div className="map-wrapper">
              <MapContainer
                center={position}
                zoom={10}
                scrollWheelZoom={true}
                className="vektor-map"
              >
                <MapUpdater position={position} />

                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <CircleMarker
                  center={position}
                  radius={11}
                  pathOptions={{
                    color: '#ff4d4d',
                    fillColor: '#ff4d4d',
                    fillOpacity: 0.8,
                  }}
                >
                  <Popup>
                    {location} — Sample monitoring location
                  </Popup>
                </CircleMarker>
              </MapContainer>
            </div>

            <p className="text-xs text-slate-500 mt-3">
              Map data from OpenStreetMap. Marker represents a sample location.
            </p>
          </div>

          {/* RELIEF APPROVAL */}
          <div className="dashboard-panel">
            <h3 className="panel-title">
              <CheckCircle className="text-emerald-400" />
              Relief Mission Approval
            </h3>

            <div className="bg-slate-800/60 rounded-xl p-5 mt-5 space-y-4">

              <div>
                <p className="text-slate-400 text-sm">Mission Name</p>
                <p className="font-semibold mt-1">
                  {location} Relief Support
                </p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Mission Status</p>

                <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm ${
                  approved
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-amber-500/20 text-amber-400'
                }`}>
                  {approved ? 'Approved (Demo)' : 'Awaiting Approval'}
                </span>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Relief Resources</p>
                <p className="mt-1">240 Sample Relief Kits</p>
              </div>

              <button
                onClick={() => setApproved(!approved)}
                className={`primary-button ${
                  approved ? 'bg-slate-600 hover:bg-slate-500' : 'bg-emerald-600 hover:bg-emerald-500'
                }`}
              >
                <CheckCircle size={17} />
                {approved ? 'Revoke Demo Approval' : 'Approve Mission'}
              </button>

              <p className="text-xs text-slate-500">
                Demonstration only. No real relief deployment is triggered.
              </p>
            </div>
          </div>

        </section>

        {/* IMAGE UPLOAD */}
        <section className="dashboard-panel">

          <h3 className="panel-title">
            <Upload className="text-cyan-400" />
            Disaster Image Analysis
          </h3>

          <p className="text-slate-400 text-sm mt-2">
            Upload a disaster photograph for sample visual analysis.
          </p>

          <label className="upload-area mt-5">
            <Upload size={30} className="text-cyan-400" />

            <span className="font-semibold mt-2">
              Click to upload an image
            </span>

            <span className="text-xs text-slate-500 mt-1">
              JPG, PNG or WEBP · Maximum 10 MB
            </span>

            <input
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={uploadImage}
              className="hidden"
            />
          </label>

          {image && (
            <div className="mt-5 bg-slate-800 rounded-xl p-4">
              <div className="flex justify-between items-center mb-3">
                <p className="text-sm font-semibold">{image.name}</p>

                <button
                  onClick={() => {
                    URL.revokeObjectURL(image.url)
                    setImage(null)
                  }}
                  className="text-red-400"
                  aria-label="Remove image"
                >
                  <X size={19} />
                </button>
              </div>

              <img
                src={image.url}
                alt="Uploaded disaster preview"
                className="image-preview"
              />

              <p className="text-xs text-amber-400 mt-3">
                Preview only. No AI analysis has been performed yet.
              </p>
            </div>
          )}

        </section>

        {/* CHAT INTERFACE */}
        <section className="dashboard-panel">

          <div className="flex items-center gap-3 mb-5">
            <div className="bg-cyan-500/20 p-3 rounded-xl">
              <Bot className="text-cyan-400" size={25} />
            </div>

            <div>
              <h3 className="text-xl font-bold">VEKTOR Assistant</h3>
              <p className="text-xs text-slate-400">
                Disaster intelligence assistant · Demo mode
              </p>
            </div>
          </div>

          <div className="chat-box space-y-4">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  item.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {item.role === 'assistant' && (
                  <Bot className="text-cyan-400 shrink-0" />
                )}

                <div className={`chat-message ${
                  item.role === 'user'
                    ? 'bg-cyan-700'
                    : 'bg-slate-800'
                }`}>
                  {item.text}
                </div>

                {item.role === 'user' && (
                  <User className="text-cyan-400 shrink-0" />
                )}
              </div>
            ))}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage()
            }}
            className="flex flex-col sm:flex-row gap-3 mt-5"
          >
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask VEKTOR about disaster conditions..."
              className="input-field flex-1"
            />

            <button type="submit" className="primary-button">
              <Send size={17} />
              Send
            </button>
          </form>

        </section>

        {/* FOOTER */}
        <footer className="border-t border-slate-800 pt-5 pb-4 text-center">
          <p className="text-cyan-400 font-bold tracking-widest">
            VEKTOR
          </p>

          <p className="text-xs text-slate-500 mt-2">
            Disaster Intelligence & Relief Coordination Platform
          </p>

          <p className="text-xs text-slate-600 mt-1">
            Hackathon prototype · Static demonstration data
          </p>
        </footer>

      </main>
    </div>
  )
}

function DashboardCard({ icon, title, value, detail, color }) {
  return (
    <div className="dashboard-card">
      <div className={`${color} mb-4`}>
        {icon}
      </div>

      <p className="text-slate-400 text-sm">{title}</p>

      <h3 className="text-xl font-bold mt-2">
        {value}
      </h3>

      <p className="text-slate-400 text-xs mt-2 leading-relaxed">
        {detail}
      </p>
    </div>
  )
}
