use std::sync::{Arc, Mutex};
use glam::{Vec3, Quat as Quaternion};
use rand::Rng;

#[derive(Debug)]
struct Transformacja3D {
    pozycja: [f64; 4],
    macierz_skalowania: [[f64; 4]; 4],
    kanały_wymiarowe: HashMap<String, f64>,
    rotacja: Quaternion,
    cząstki: Vec<CzastkaKwantowa>,
    entanglacje: Vec<Arc<Mutex<SplątanieKwantowe>>>,
    deformacja_nieliniowa: Box<dyn Fn([f64; 4]) -> [f64; 4]>
}

impl Transformacja3D {
    fn nowa() -> Self {
        Transformacja3D {
            pozycja: [0.0; 4],
            macierz_skalowania: [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            kanały_wymiarowe: HashMap::from([
                ("Entropia".into(), 0.0),
                ("Potencjał".into(), 1.0),
            ]),
            rotacja: Quaternion::IDENTITY,
            cząstki: Vec::new(),
            entanglacje: Vec::new(),
            deformacja_nieliniowa: Box::new(|x| x)
        }
    }

    fn aplikuj_deformacje(&mut self, wektor: [f64; 4]) {
        let wektor_zdeformowany = (self.deformacja_nieliniowa)(wektor);
        self.pozycja.iter_mut().enumerate().for_each(|(i, p)| {
            *p += self.macierz_skalowania[i].iter().zip(wektor_zdeformowany.iter())
                .fold(0.0, |acc, (m, v)| acc + m * v);
        });
        self.propaguj_entanglacje();
    }
}

impl Transformacja3D {
    fn aktualizuj_animacje(&mut self, delta_czasu: f64) {
        self.rotacja *= Quaternion::from_axis_angle(Vec3::Z, delta_czasu * 0.5);
        self.emituj_cząstki(delta_czasu);
        self.aktualizuj_cząstki(delta_czasu);
    }

    fn emituj_cząstki(&mut self, intensywność: f64) {
        let nowe_cząstki = (0..(intensywność * 10.0) as usize).map(|_| CzastkaKwantowa {
            pozycja: self.pozycja,
            prędkość: Vec3::new(
                rand::random::<f32>() - 0.5,
                rand::random::<f32>() - 0.5,
                rand::random::<f32>() - 0.5,
            ).normalize() * 0.1,
            żywotność: 1.0,
        });
        self.cząstki.extend(nowe_cząstki);
    }

    fn aktualizuj_cząstki(&mut self, delta_czasu: f64) {
        self.cząstki.iter_mut().for_each(|cząstka| {
            cząstka.aktualizuj(delta_czasu);
        });
        self.cząstki.retain(|cząstka| cząstka.czy_aktywna());
    }

    fn propaguj_entanglacje(&mut self) {
        for entanglacja in self.entanglacje.iter_mut() {
            if let Ok(mut e) = entanglacja.lock() {
                e.aktualizuj_entanglacje(0.016);
            }
        }
    }

    fn dodaj_entanglacje(&mut self, entanglacja: SplątanieKwantowe) {
        self.entanglacje.push(Arc::new(Mutex::new(entanglacja)));
    }

    fn ustaw_deformacje(&mut self, f: impl Fn([f64; 4]) -> [f64; 4] + 'static) {
        self.deformacja_nieliniowa = Box::new(f);
    }
}