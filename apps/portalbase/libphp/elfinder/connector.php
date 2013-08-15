<?php


error_reporting(0); // Set E_ALL for debuging

include_once dirname(__FILE__).DIRECTORY_SEPARATOR.'elFinderConnector.class.php';
include_once dirname(__FILE__).DIRECTORY_SEPARATOR.'elFinder.class.php';
include_once dirname(__FILE__).DIRECTORY_SEPARATOR.'elFinderVolumeDriver.class.php';
include_once dirname(__FILE__).DIRECTORY_SEPARATOR.'elFinderVolumeLocalFileSystem.class.php';
// Required for MySQL storage connector
// include_once dirname(__FILE__).DIRECTORY_SEPARATOR.'elFinderVolumeMySQL.class.php';
// Required for FTP connector support
// include_once dirname(__FILE__).DIRECTORY_SEPARATOR.'elFinderVolumeFTP.class.php';


/**
 * Simple function to demonstrate how to control file access using "accessControl" callback.
 * This method will disable accessing files/folders starting from  '.' (dot)
 *
 * @param  string  $attr  attribute name (read|write|locked|hidden)
 * @param  string  $path  file path relative to volume root directory started with directory separator
 * @return bool|null
 **/
 
function access2($attr, $path, $data, $volume) {	
	//echo ($path."\n");
	logg("acces:".$path);
	if (strpos(basename($path), '.') == 0) 
	{	       // if file/folder begins with '.' (dot)
		if (strstr(basename($path), '.') <>False)
		{
			//echo ($path." punt"."\n");
			return  !($attr == 'read' || $attr == 'write');    // set read+write to false, other (locked+hidden) set to true
		}		
	}
	if (preg_match ("/\.pyc$/",$path )==1)
	{	    
		//echo ($path." pyc"."\n");	
		 return !($attr == 'read' || $attr == 'write');
	}	
	return null;
}

function access($attr, $path, $data, $volume) {
	//return 0;
	return strpos(basename($path), '.') === 0       // if file/folder begins with '.' (dot)
		? !($attr == 'read' || $attr == 'write')    // set read+write to false, other (locked+hidden) set to true
		:  null;                                    // else elFinder decide it itself
}

function getPath(){    
	$rootpath=$_GET["rootpath"];	 
	 $rootpath='{root}'.$rootpath."/";
	 xdebug_enable();
	xdebug_break();
	xdebug_debug_zval_stdout( $_GET);
	logg("rootpath:".$rootpath);
	return $rootpath;
}

function logg($msg){
    return
	$fp = fopen('c:/temp/phplog.txt', 'a');
	fwrite($fp,$msg."\n");
	fclose($fp);
}

$opts = array(
	'debug' => false,
	'roots' => array(
		array(
			'driver'        => 'LocalFileSystem',   // driver for accessing file system (REQUIRED)
			'path'          => '{path}',         // path to files (REQUIRED)
			'URL'           =>  '/root/{rootdownload}', // URL to files (REQUIRED),
			//'alias' => '.',
			//'startPath' => '',
			'mimeDetect' => 'internal',
			//'mimefile' =>  'c:/qb6/apps/acloudEventHandler/',
			'attributes' => array(
				array(
					'pattern' => '/pyc$/', //You can also set permissions for file types by adding, for example, .jpg inside pattern.
					'read'    => false,
					'write'   => false,
					'locked'  => true
				)
			),
			'accessControl' => 'access2'             // disable and hide dot starting files (OPTIONAL)
		)
	)
);

// run elFinder
$connector = new elFinderConnector(new elFinder($opts));
$connector->run();

