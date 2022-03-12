from django.db import models
from django.urls import reverse
from django.utils import timezone

from django.db import models
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

# Create your models here.
class ChartRun(models.Model):
    date =  models.DateTimeField('date run')

    class Meta:
        ordering = ['-date'] 

class Chart(models.Model):
    BW_SURFACE = 1
    TYPES_OF_CHART = [
        (BW_SURFACE, 'black and white - surface pressure')
    ]
    type = models.IntegerField('type', choices = TYPES_OF_CHART, default = BW_SURFACE)
    run = models.ForeignKey(ChartRun,on_delete=models.CASCADE, default=0)
    valid_from = models.DateTimeField('valid from') 
    valid_to = models.DateTimeField('valid to')
    image_url = models.URLField('Met office URL', max_length=200)
    image_file = models.ImageField(upload_to='charts/%Y/%m/%d/', blank=True)
    forecast_time = models.DateTimeField('date')

    def save(self, *args, **kwargs):
        if self.image_url and not self.image_file:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.image_url).read())
            img_temp.flush()
            fname = self.forecast_time.strftime('%Y%m%d%H%M%S') +'.gif'
            self.image_file.save(fname, File(img_temp))
        super(Chart, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('chart:chart_detail',
                       args=[str(self.id)] ) 
    
    class Meta:
        ordering = ['-forecast_time']

class SatelliteImage(models.Model):
    NONE = 0
    SATELLITE_VISIBLE_N = 1
    SATELLITE_INFRARED = 2
    RADAR_COMPOSITE = 3 
    ATDNET = 4
    TYPES_OF_IMAGE = [
        (NONE, 'Unknown'),
        (SATELLITE_VISIBLE_N, 'SATELLITE_Visible_N_Section'),
        (SATELLITE_INFRARED, 'SATELLITE_Infrared_Fulldisk'),
        (RADAR_COMPOSITE, 'RADAR_UK_Composite_Highres'),
        (ATDNET, 'ATDNET_Sferics'),
    ]

    type_code = models.IntegerField('type_code', choices = TYPES_OF_IMAGE, default = NONE)
    image_time = models.DateTimeField('image time',default=timezone.now)
    image_url = models.URLField('Met office URL', max_length=200)
    image_file = models.ImageField(upload_to='satellite/%Y/%m/%d/', blank=True)
    
    def save(self, *args, **kwargs):
        if self.image_url and not self.image_file:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.image_url).read())
            img_temp.flush()
            # work out layername from the type_code
            layername = 'unknown'
            for ii in self.TYPES_OF_IMAGE:
                type_code, layername_check = ii
                if type_code == self.type_code:
                    layername = layername_check
                    break
            fname = layername  +'_' + self.image_time.strftime('%Y%m%d%H%M%S') +'.png'
            self.image_file.save(fname, File(img_temp))
            
        super(SatelliteImage, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('chart:satelliteimage_detail',
                       args=[str(self.id)] )    
    class Meta:
       ordering = ['-image_time']

#def get_remote_image(self):
#    if self.image_url and not self.image_file:
#        img_temp = NamedTemporaryFile(delete=True)
#        img_temp.write(urlopen(self.image_url).read())
#        img_temp.flush()
#        self.image_file.save(f"image_{self.pk}", File(img_temp))
#    self.save()
