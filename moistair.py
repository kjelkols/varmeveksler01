class AirProperties:
    def __init__(self, temperature_c: float, phi: float, pressure: float) -> None:
        self.temperature_c = temperature_c
        self.phi = phi
        self.pressure = pressure
        self.rho = float("nan")
        self.dynamic_viscosity = float("nan")
        self.cp = float("nan")
        self.k = float("nan")
        self.prandtl = float("nan")
        self._calculate()
        
    @staticmethod
    def from_dict(data: dict) -> 'AirProperties':
        return AirProperties(
            temperature_c=data['temperature_c'],
            phi=data['phi'],
            pressure=data['pressure']
        )

    def _calculate(self) -> None:
        """
        Beregn og sett luftens egenskaper som attributter.
        """
        T_k = self.temperature_c + 273.15  # Kelvin
        # Ideell gasslov for tetthet
        self.rho = self.pressure / (287.05 * T_k)
        # Sutherland's formel for viskositet
        mu_ref = 1.716e-5
        T0 = 273.15
        S = 110.4
        self.dynamic_viscosity = mu_ref * ((T0 + S) / (T_k + S)) * ((T_k / T0) ** 1.5)
        # Spesifikk varmekapasitet
        self.cp = 1005 + 0.05 * (self.temperature_c - 20)
        # Termisk konduktivitet
        self.k = 0.024 + 0.00007 * self.temperature_c
        # Prandtl-tall
        self.prandtl = 0.7 + 0.0002 * self.temperature_c

class AirStream:
    def __init__ (self, m_dot: float, air_properties: AirProperties) -> None:
        self.m_dot = m_dot
        self.air = air_properties

    @staticmethod
    def from_dict(data: dict) -> 'AirStream':
        air_props = AirProperties(
            temperature_c=data['temperature_c'],
            phi=data['phi'],
            pressure=data['pressure']
        )
        return AirStream(m_dot=data['mass_flow_rate'], air_properties=air_props)
    
    @property
    def mass_flow_rate(self) -> float:
        return self.m_dot
    @property
    def temperature_c(self) -> float:
        return self.air.temperature_c
    @property
    def phi(self) -> float:
        return self.air.phi
    @property
    def pressure(self) -> float:
        return self.air.pressure
    @property
    def rho(self) -> float:
        return self.air.rho
    @property
    def dynamic_viscosity(self) -> float:
        return self.air.dynamic_viscosity
    @property
    def cp(self) -> float:
        return self.air.cp
    @property
    def k(self) -> float:
        return self.air.k
    @property
    def prandtl(self) -> float:
        return self.air.prandtl

if __name__ == "__main__":  
    air_props = AirProperties(25, 0.5, 101325)
    air_stream = AirStream(1.2, air_props)
    print(f"Mass flow rate: {air_stream.mass_flow_rate} kg/s")
    print(f"Temperature: {air_stream.temperature_c} °C")
    print(f"Density: {air_stream.rho} kg/m³")
    print(f"Dynamic Viscosity: {air_stream.dynamic_viscosity} Pa·s")
    print(f"Specific Heat Capacity: {air_stream.cp} J/(kg·K)")
    print(f"Thermal Conductivity: {air_stream.k} W/(m·K)")
    print(f"Prandtl Number: {air_stream.prandtl}")