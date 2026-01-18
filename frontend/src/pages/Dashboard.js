import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Plus, LogOut, Trash2, MapPin, Building2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      const response = await axios.get(`${API_URL}/properties`);
      setProperties(response.data);
    } catch (err) {
      setError('Fehler beim Laden der Properties');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProperty = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
      await axios.post(`${API_URL}/properties`, {
        name: formData.get('name'),
        description: formData.get('description'),
        address: formData.get('address'),
      });
      setDialogOpen(false);
      fetchProperties();
      e.target.reset();
    } catch (err) {
      setError(err.response?.data?.detail || 'Fehler beim Erstellen');
    }
  };

  const handleDeleteProperty = async (id) => {
    if (!window.confirm('Property wirklich löschen?')) return;
    
    try {
      await axios.delete(`${API_URL}/properties/${id}`);
      fetchProperties();
    } catch (err) {
      setError('Fehler beim Löschen');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Welcome Link</h1>
            <p className="text-sm text-gray-600">
              Willkommen, {user?.name || user?.email}
            </p>
          </div>
          <Button variant="outline" onClick={logout}>
            <LogOut className="mr-2 h-4 w-4" />
            Abmelden
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Gesamt Properties</CardDescription>
              <CardTitle className="text-3xl">{properties.length}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Aktive Links</CardDescription>
              <CardTitle className="text-3xl">{properties.length}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Besucher (Monat)</CardDescription>
              <CardTitle className="text-3xl">0</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Meine Properties</h2>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Neue Property
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <form onSubmit={handleCreateProperty}>
                <DialogHeader>
                  <DialogTitle>Neue Property erstellen</DialogTitle>
                  <DialogDescription>
                    Fügen Sie eine neue Immobilie oder Location hinzu
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      name="name"
                      placeholder="z.B. Hotel Alpenblick"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="address">Adresse</Label>
                    <Input
                      id="address"
                      name="address"
                      placeholder="Straße, PLZ Ort"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Beschreibung</Label>
                    <Textarea
                      id="description"
                      name="description"
                      placeholder="Beschreiben Sie Ihre Property..."
                      rows={4}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">Property erstellen</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Properties Grid */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Lädt Properties...</p>
          </div>
        ) : properties.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent className="pt-6">
              <Building2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Noch keine Properties
              </h3>
              <p className="text-gray-600 mb-4">
                Erstellen Sie Ihre erste Property, um loszulegen
              </p>
              <Button onClick={() => setDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Erste Property erstellen
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((property) => (
              <Card key={property.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-start justify-between">
                    <span className="line-clamp-1">{property.name}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteProperty(property.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </CardTitle>
                  {property.address && (
                    <CardDescription className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {property.address}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {property.description || 'Keine Beschreibung vorhanden'}
                  </p>
                </CardContent>
                <CardFooter className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Link kopieren
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    Bearbeiten
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
